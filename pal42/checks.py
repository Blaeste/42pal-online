"""Checks made on the student's compiled code, beyond its output.

They read the symbols of the student's objects (.o) with nm: the library
functions called, to refuse the forbidden ones, and whether a main is
defined. They also run the program under valgrind, for leaks and memory
errors. For Python, they read the student's source instead: the modules
imported and the functions called. Like the rest of the core, this module
never prints.
"""

import ast
import re
import subprocess
import tempfile
from pathlib import Path

from pal42.runners.base import run_command

def used_functions(*files, nm="nm"):
	"""Return the names of the library functions that `files` call.

	files are objects or programs. A function defined in one of them (one
	student file calling another) is not counted. Names starting with _
	belong to the C runtime (__libc_start_main...), not to the student's code.
	Without nm on the machine, the check cannot be made: nothing is listed,
	so nothing is refused.
	"""
	undefined = _symbols(files, nm, "-u", kind="U")
	if undefined is None:
		return set()
	defined = _symbols(files, nm, "--defined-only")
	return {name for name in undefined - defined if not name.startswith("_")}

# The functions gcc and clang call on their own: memset for "int tab[512] =
# {0};", memcpy for a copy of a struct or of a local table. Found by nm, they
# only count when the student's code names them.
COMPILER_CALLS = {"memset", "memcpy", "memmove"}

# What is not code in C: comments, then strings and characters (escapes kept in).
NOT_CODE = re.compile(r"""//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'""", re.DOTALL)

def named_in_code(name, sources):
	"""True if one of the C `sources` names the function `name` in its code.

	Comments, strings and characters do not count; __builtin_name does.
	"""
	pattern = re.compile(rf"\b(?:__builtin_)?{re.escape(name)}\b")
	for source in sources:
		try:
			code = NOT_CODE.sub(" ", Path(source).read_text(encoding="utf-8", errors="replace"))
		except OSError:
			continue
		if pattern.search(code):
			return True
	return False

def written_calls(used, sources):
	"""The names of `used` the student really calls: without the compiler's own calls."""
	return {name for name in used if name not in COMPILER_CALLS or named_in_code(name, sources)}

def defines_main(*files, nm="nm"):
	"""True when `files` define a main: a function rendu must not have one."""
	return "main" in (_symbols(files, nm, "--defined-only") or set())

def _symbols(files, nm, option, kind=None):
	"""Return the symbol names nm lists with `option`, or None without nm.

	nm prints one symbol per line: "U printf@GLIBC_2.2.5" for an undefined
	one, "0000000000001139 T main" for a defined one; the letter before the
	name is its kind. kind keeps only one kind; the @version is dropped.
	"""
	try:
		process = subprocess.run([nm, option, *map(str, files)], capture_output=True, text=True)
	except FileNotFoundError:
		return None
	names = set()
	for line in process.stdout.splitlines():
		parts = line.split()
		# Lines with one word are the "file.o:" headers nm adds for several files.
		if len(parts) >= 2 and (kind is None or parts[-2] == kind):
			names.add(parts[-1].split("@")[0])
	return names

# Exit code valgrind is asked to give when it finds a leak or a memory error.
VALGRIND_ERROR = 42

def memory_report(program, test, timeout=30.0, valgrind="valgrind"):
	"""Return what valgrind says about `program` run on `test`.

	"" when every allocation is freed and no memory error is seen; otherwise
	the report (leaks, invalid reads or writes...), without valgrind's ==pid==
	marks. None when valgrind is not on the machine: nothing could be checked.
	The timeout is long: a program runs much slower under valgrind.
	"""
	with tempfile.TemporaryDirectory() as tmp:
		# The report goes to a file: run_command does not keep stderr.
		log = Path(tmp) / "valgrind.log"
		argv = [
			valgrind, "-q", "--leak-check=full",
			# Only the memory really lost counts, not "still reachable".
			"--errors-for-leak-kinds=definite,indirect",
			f"--error-exitcode={VALGRIND_ERROR}", f"--log-file={log}",
			str(program), *test.args,
		]
		try:
			result = run_command(argv, test.stdin, timeout)
		except FileNotFoundError:
			return None
		if result.exit_code != VALGRIND_ERROR:
			return ""
		text = log.read_text(encoding="utf-8", errors="replace")
	# Each line starts with ==12345==, the number of the process: dropped.
	lines = [re.sub(r"^==\d+== ?", "", line) for line in text.splitlines()]
	return "\n".join(lines).strip("\n") + "\n"

# Modules any Python file may import: type hints and future syntax only.
ALWAYS_IMPORTABLE = {"typing", "__future__"}

# Calls that import or run other code: counted like an import.
IMPORT_CALLS = {"__import__", "exec", "eval", "compile"}

def python_violations(sources, allowed_imports=(), forbidden_calls=()):
	"""Return what the Python `sources` use without the right, sorted.

	"import x" for each module imported that is not in allowed_imports (nor
	typing or __future__), and "name()" for each call of a name in
	forbidden_calls, as a function (sorted(x)) or as a method (x.sort()),
	and of __import__, exec, eval or compile. The source is read, not run:
	comments and strings do not count. The sources must parse (the runner
	checked their syntax first).
	"""
	allowed = set(allowed_imports) | ALWAYS_IMPORTABLE
	found = set()
	for source in sources:
		tree = ast.parse(Path(source).read_text(encoding="utf-8"))
		for node in ast.walk(tree):
			if isinstance(node, ast.Import):
				found.update(f"import {alias.name}" for alias in node.names
					if alias.name.split(".")[0] not in allowed)
			elif isinstance(node, ast.ImportFrom):
				# node.level > 0: a relative import (from . import x).
				if node.level or (node.module or "").split(".")[0] not in allowed:
					found.add(f"import {'.' * node.level}{node.module or ''}")
			elif isinstance(node, ast.Call):
				function = node.func
				if isinstance(function, ast.Name):
					name = function.id
				elif isinstance(function, ast.Attribute):
					name = function.attr
				else:
					continue
				if name in forbidden_calls or name in IMPORT_CALLS:
					found.add(f"{name}()")
	return sorted(found)
