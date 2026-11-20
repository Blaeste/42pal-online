"""The C runner: compiles a student's .c files like the moulinette."""

import shutil
import subprocess
from pathlib import Path

from pal42.runners.base import DEFAULT_TIMEOUT, MAX_OUTPUT, CompileResult, run_command

# The flags of the moulinette; an exam can give its own command instead.
DEFAULT_COMMAND = ("cc", "-Wall", "-Wextra", "-Werror")

class CRunner:
	"""Compiles C files with a compile command (DEFAULT_COMMAND by default)."""

	def __init__(self, command=DEFAULT_COMMAND, timeout=DEFAULT_TIMEOUT):
		self.command = tuple(command)
		# Seconds the student's program may run on one test.
		self.timeout = timeout

	def command_line(self, files, name):
		"""The command a compilation trace shows: cc ... files -o name."""
		return " ".join([*self.command, *files, "-o", name])

	def compile(self, sources, workdir, name, extra=()):
		"""Compile `sources` (the student's files) into the program workdir/name.

		Two steps: the sources are compiled into objects (cc -c), one per file,
		kept in result.objects so that the checks look at the student's code
		only; then the objects are linked, with the `extra` sources (a test
		main) if any. The files are copied into workdir and compiled there, by
		their own names: the errors read "bad.c:3:6", without the folder, and
		the student's folder is left untouched. Headers among the files are
		copied, not compiled.
		"""
		workdir = Path(workdir)
		# Every file is copied, headers too (for #include "..."), but only the
		# .c files are compiled.
		names = [name for name in _copy_into(sources, workdir) if name.endswith(".c")]
		extra_names = [name for name in _copy_into(extra, workdir) if name.endswith(".c")]
		objects = tuple(workdir / (Path(source).stem + ".o") for source in names)
		steps = [
			# -g: debug information, so that valgrind can give the line of a
			# leak (prog.c:7); it changes neither the warnings nor the program.
			[*self.command, "-g", "-c", *names],
			[*self.command, *(obj.name for obj in objects), *extra_names, "-o", name],
		]
		output = ""
		for number, step in enumerate(steps):
			try:
				process = subprocess.run(step, cwd=workdir, capture_output=True, text=True)
			# The command of an exam may name a compiler this machine lacks.
			except FileNotFoundError:
				return CompileResult(False, f"compiler not found: {self.command[0]}", None)
			output += process.stdout + process.stderr
			if process.returncode != 0:
				# If only the link failed, the objects exist: keep them, so that
				# the grader can tell why (a main in a function rendu...).
				return CompileResult(False, output, None, objects if number == 1 else ())
		return CompileResult(True, output, workdir / name, objects)

	def run(self, program, test, max_output=MAX_OUTPUT):
		"""Run the compiled `program` on `test`: its arguments and standard input."""
		return run_command([str(program), *test.args], test.stdin, self.timeout, max_output)

def _copy_into(files, workdir):
	"""Copy `files` into workdir (unless already there) and return their names."""
	for file in files:
		# resolve() gives the full path, so the same folder is recognized
		# however it is written; a file already there needs no copy.
		if Path(file).resolve().parent != workdir.resolve():
			shutil.copy(file, workdir)
	return [Path(file).name for file in files]
