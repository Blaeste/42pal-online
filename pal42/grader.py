"""The grader: checks a student's rendu against the oracle, like the moulinette.

It compiles the rendu in a temporary folder, runs each test of the variant,
and stops at the first one whose output differs from the oracle's. Like the
rest of the core, it never prints: the trace comes back as text.
"""

import random
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pal42 import checks, trace
from pal42.subject import test_command

# valgrind is slow (about 0.4 s a test): leaks are checked on this many tests
# at most, the first ones, which are the fixed edge cases of an exercise.
MAX_LEAK_TESTS = 6

# The test main of a function exercise, written next to the student's files.
HARNESS_FILES = {"c": "main_42pal.c", "python": "main_42pal.py"}

@dataclass(frozen=True)
class Grade:
	"""The result of a grademe.

	passed tells whether every test passed; trace explains the first failure
	(empty when passed); tests_passed counts the tests passed before it.
	"""
	passed: bool
	trace: str
	tests_passed: int
	tests_total: int
	# What could not be checked (valgrind missing...): the front-ends show it.
	warnings: tuple[str, ...] = ()

def grade(variant, rendu, runner, progress=None, valgrind="valgrind"):
	"""Grade the files of `rendu` (the student's folder) for `variant`.

	In order: the expected files must be there, they must compile, they must
	call no forbidden function, then each test must neither crash nor time
	out, and print what the oracle says.
	The first failure stops the grading and gives the trace.
	progress(number, total), if given, is called before each test: the
	front-ends use it to show how far the grading is. When the exercise
	checks leaks, the tests are then run again under valgrind, and progress
	gets a third argument, "memory".
	"""
	exo = variant.exercise
	# The tests depend on the variant's seed: grading twice runs the same ones.
	tests = exo.generate_tests(variant.params, random.Random(variant.seed))
	sources = [Path(rendu) / file for file in variant.expected_files]
	missing = [source.name for source in sources if not source.is_file()]
	if missing:
		return Grade(False, trace.missing_trace(missing), 0, len(tests))
	with tempfile.TemporaryDirectory() as work:
		# Compiled with the student's files: the files given by the exercise,
		# and the test main of a function exercise.
		extra = []
		for name, content in variant.provided_files.items():
			extra.append(Path(work) / name)
			extra[-1].write_text(content, encoding="utf-8")
		if exo.kind == "function":
			extra.append(Path(work) / HARNESS_FILES[exo.language])
			extra[-1].write_text(variant.harness, encoding="utf-8")
		compiled = runner.compile(sources, work, variant.name, extra=extra)
		if not compiled.ok:
			if exo.kind == "function" and compiled.objects and checks.defines_main(*compiled.objects):
				return Grade(False, trace.main_trace(), 0, len(tests))
			text = trace.compile_trace(
				runner.command_line(variant.expected_files, variant.name), compiled.output
			)
			return Grade(False, text, 0, len(tests))
		program = compiled.binary
		forbidden = _forbidden(exo, compiled, sources)
		if forbidden:
			return Grade(False, forbidden, 0, len(tests))
		for number, test in enumerate(tests, start=1):
			if progress:
				progress(number, len(tests))
			result = runner.run(program, test)
			if result.timed_out or result.signal:
				text = trace.crash_trace(number, test_command(variant, test), result)
				return Grade(False, text, number - 1, len(tests))
			expected = exo.oracle(variant.params, test)
			if result.stdout != expected.encode():
				text = trace.diff_trace(number, test_command(variant, test), result.stdout, expected)
				return Grade(False, text, number - 1, len(tests))
		if exo.check_leaks:
			return _check_leaks(variant, program, tests, progress, valgrind)
	return Grade(True, "", len(tests), len(tests))

def _forbidden(exo, compiled, sources):
	"""The trace of what the rendu uses without the right, or "" if nothing."""
	if exo.language == "python":
		found = checks.python_violations(sources, exo.allowed_imports, exo.forbidden_calls)
		if found:
			return trace.python_forbidden_trace(found, exo.allowed_imports, exo.forbidden_calls)
		return ""
	# Only the student's objects: the test main may use printf. And only
	# what the student calls: not the memset the compiler adds for = {0}.
	used = checks.written_calls(checks.used_functions(*compiled.objects), sources)
	forbidden = sorted(used - set(exo.allowed_functions))
	if forbidden:
		return trace.forbidden_trace(forbidden, exo.allowed_functions)
	return ""

def _check_leaks(variant, program, tests, progress, valgrind):
	"""Run the first MAX_LEAK_TESTS tests under valgrind; a leak or memory error fails.

	Only called once every output is right: valgrind is slow.
	"""
	checked = tests[:MAX_LEAK_TESTS]
	for number, test in enumerate(checked, start=1):
		if progress:
			progress(number, len(checked), "memory")
		report = checks.memory_report(program, test, valgrind=valgrind)
		if report is None:
			warning = "valgrind not found: memory leaks were not checked"
			return Grade(True, "", len(tests), len(tests), (warning,))
		if report:
			text = trace.leak_trace(number, test_command(variant, test), report)
			return Grade(False, text, number - 1, len(tests))
	return Grade(True, "", len(tests), len(tests))
