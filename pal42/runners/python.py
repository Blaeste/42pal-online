"""The Python runner: checks a student's .py files, then runs them with python3.

There is nothing to build: "compiling" checks the syntax of each file
(python3 -m py_compile), so that a syntax error gets a trace of its own,
like a compilation error in C. Running starts python3 on the test main of a
function exercise, which imports the student's file, or on the student's
file itself for a program.
"""

import shutil
import subprocess
from pathlib import Path

from pal42.runners.base import DEFAULT_TIMEOUT, MAX_OUTPUT, CompileResult, run_command
from pal42.runners.c import _copy_into

# The interpreter of an exam that names none; an exam gives its own in "compile".
DEFAULT_COMMAND = ("python3",)

# -B: no __pycache__ written; -E and -s: neither PYTHON* variables nor the
# user's own packages change how the student's code runs.
RUN_FLAGS = ("-B", "-E", "-s")

class PythonRunner:
	"""Checks and runs Python files with an interpreter command (python3 by default)."""

	def __init__(self, command=DEFAULT_COMMAND, timeout=DEFAULT_TIMEOUT):
		self.command = tuple(command)
		# Seconds the student's code may run on one test.
		self.timeout = timeout

	def command_line(self, files, name):
		"""The command a compilation trace shows: the syntax check of the files."""
		return " ".join([*self.command, "-m", "py_compile", *files])

	def compile(self, sources, workdir, name, extra=()):
		"""Copy the files into workdir and check the syntax of the student's ones.

		The files are checked there, by their own names: the errors read
		File "bad.py", without the folder, and the student's folder is left
		untouched. The program to run (result.binary) is the test main among
		the `extra` files if there is one, else the first student file.
		"""
		workdir = Path(workdir)
		names = _copy_into(sources, workdir)
		extra_names = [name for name in _copy_into(extra, workdir) if name.endswith(".py")]
		step = [*self.command, "-m", "py_compile", *names]
		try:
			process = subprocess.run(step, cwd=workdir, capture_output=True, text=True)
		except FileNotFoundError:
			return CompileResult(False, f"interpreter not found: {self.command[0]}", None)
		output = process.stdout + process.stderr
		if process.returncode != 0:
			return CompileResult(False, output, None)
		shutil.rmtree(workdir / "__pycache__", ignore_errors=True)
		return CompileResult(True, output, workdir / (extra_names or names)[0])

	def run(self, program, test, max_output=MAX_OUTPUT):
		"""Run the file `program` on `test`: its arguments and standard input."""
		argv = [*self.command, *RUN_FLAGS, str(program), *test.args]
		return run_command(argv, test.stdin, self.timeout, max_output)
