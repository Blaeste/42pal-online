"""Runners: compile and run a student's files, one runner per language."""

from pal42.runners.c import CRunner
from pal42.runners.python import PythonRunner

def runner_for(language, command=None):
	"""The runner of `language`, with the compile command of the exam if given.

	command is the "compile" of an exam: the compiler and its flags for C,
	the interpreter for Python. None gives the runner's own default.
	"""
	runner = PythonRunner if language == "python" else CRunner
	return runner(command) if command else runner()
