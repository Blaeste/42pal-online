"""Tests of the Python grading: the runner, the test main, the checks of the
source, and a whole grademe of a made-up Python exercise.

Run all the tests from the project root with: python3 -m unittest -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

from pal42 import python_exercise as py
from pal42.checks import python_violations
from pal42.grader import grade
from pal42.model import ExerciseError, TestCase
from pal42.runners import runner_for
from pal42.runners.c import CRunner
from pal42.runners.python import PythonRunner
from pal42.subject import render
from pal42.variant import Variant
from tests.helpers import make_exercise

PYTHON = (sys.executable,)

class Folders(unittest.TestCase):
	"""Each test gets a folder for the student's files and a work folder."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.rendu = Path(self.tmp.name) / "rendu"
		self.work = Path(self.tmp.name) / "work"
		self.rendu.mkdir()
		self.work.mkdir()

	def tearDown(self):
		self.tmp.cleanup()

	def write(self, name, code, folder=None):
		path = (folder or self.rendu) / name
		path.write_text(code, encoding="utf-8")
		return path

class TestPythonRunner(Folders):
	"""PythonRunner: compile checks the syntax, run starts python3 on a file."""

	def test_a_right_file_compiles_and_runs_with_its_arguments(self):
		source = self.write("echo.py", "import sys\nprint(' '.join(sys.argv[1:]))\n")
		result = PythonRunner(PYTHON).compile([source], self.work, "echo")
		self.assertTrue(result.ok, result.output)
		self.assertEqual(result.binary, self.work / "echo.py")
		run = PythonRunner(PYTHON).run(result.binary, TestCase(("a", "b c")))
		self.assertEqual(run.stdout, b"a b c\n")

	def test_a_syntax_error_fails_naming_the_file_without_its_folder(self):
		source = self.write("bad.py", "def f(:\n\treturn 1\n")
		result = PythonRunner(PYTHON).compile([source], self.work, "bad")
		self.assertFalse(result.ok)
		self.assertIsNone(result.binary)
		self.assertIn("SyntaxError", result.output)
		self.assertIn("bad.py", result.output)
		self.assertNotIn(self.tmp.name, result.output)

	def test_a_test_main_given_with_the_files_is_the_one_run(self):
		source = self.write("double.py", "def double(n):\n\treturn 2 * n\n")
		main = self.write("main_42pal.py", py.harness("double"), self.work)
		result = PythonRunner(PYTHON).compile([source], self.work, "double", extra=[main])
		self.assertEqual(result.binary, self.work / "main_42pal.py")
		run = PythonRunner(PYTHON).run(result.binary, py.case(21))
		self.assertEqual(run.stdout, b"42\n")

	def test_an_endless_loop_times_out(self):
		source = self.write("loop.py", "while True:\n\tpass\n")
		runner = PythonRunner(PYTHON, timeout=0.5)
		result = runner.compile([source], self.work, "loop")
		self.assertTrue(runner.run(result.binary, TestCase()).timed_out)

	def test_the_command_line_shown_in_a_trace(self):
		self.assertEqual(PythonRunner(("python3",)).command_line(["a.py"], "a"),
			"python3 -m py_compile a.py")
		self.assertEqual(CRunner().command_line(["a.c"], "a"), "cc -Wall -Wextra -Werror a.c -o a")

class TestRunnerFor(unittest.TestCase):
	def test_one_runner_per_language(self):
		self.assertIsInstance(runner_for("c", ("gcc",)), CRunner)
		self.assertEqual(runner_for("c", ("gcc",)).command, ("gcc",))
		self.assertIsInstance(runner_for("python"), PythonRunner)
		self.assertEqual(runner_for("python", ("python3",)).command, ("python3",))

class TestHarness(Folders):
	"""The test main prints repr() of what the function returns, or what went wrong."""

	def run_main(self, code, *values):
		source = self.write("pick.py", code)
		main = self.write("main_42pal.py", py.harness("pick"), self.work)
		runner = PythonRunner(PYTHON)
		result = runner.compile([source], self.work, "pick", extra=[main])
		return runner.run(result.binary, py.case(*values)).stdout.decode()

	def test_values_go_in_as_python_literals_and_come_out_with_repr(self):
		code = "def pick(items, n):\n\treturn [item for item in items if len(item) == n]\n"
		self.assertEqual(self.run_main(code, ["ab", "c", "de"], 2), "['ab', 'de']\n")

	def test_an_exception_is_said(self):
		code = "def pick(items, n):\n\treturn items[n]\n"
		self.assertEqual(self.run_main(code, [], 3),
			"Your function raised IndexError: list index out of range\n")

	def test_a_missing_function_is_said(self):
		self.assertEqual(self.run_main("def other():\n\tpass\n", 1), "pick.py has no function pick\n")

COUNTER = """class Counter:
	def __init__(self, start):
		self.value = start

	def add(self, n):
		self.value += n

	def get(self):
		return self.value
"""

class TestClassHarness(Folders):
	"""A class: the test main builds an object, calls its methods, prints their results."""

	def run_main(self, code, test):
		source = self.write("count_up.py", code)
		main = self.write("main_42pal.py", py.class_harness("count_up", "Counter"), self.work)
		runner = PythonRunner(PYTHON)
		result = runner.compile([source], self.work, "count_up", extra=[main])
		return runner.run(result.binary, test).stdout.decode()

	def test_each_call_gives_its_result_in_a_list(self):
		test = py.class_case([10], [["add", 5], ["get"], ["add", -1], ["get"]])
		self.assertEqual(self.run_main(COUNTER, test), "[None, 15, None, 14]\n")

	def test_a_missing_method_or_an_exception_is_said(self):
		self.assertEqual(self.run_main(COUNTER, py.class_case([1], [["get"], ["reset"]])),
			"Counter has no method reset (call 2)\n")
		self.assertEqual(self.run_main(COUNTER, py.class_case(["x"], [["add", 1]])),
			"add() raised TypeError: can only concatenate str (not \"int\") to str (call 1)\n")
		self.assertEqual(self.run_main("class Other:\n\tpass\n", py.class_case([], [])),
			"count_up.py has no class Counter\n")

	def test_the_call_shown_builds_the_object_then_calls(self):
		call = py.class_call("Counter")
		test = py.class_case([10], [["add", 5], ["get"]])
		self.assertEqual(call("count_up", test), "o = Counter(10); [o.add(5), o.get()]")
		self.assertEqual(py.class_values(test), ([10], [["add", 5], ["get"]]))

class TestHelpers(unittest.TestCase):
	def test_case_values_call_and_shown(self):
		test = py.case([1, 2], "a b", True)
		self.assertEqual(test.args, ("[1, 2]", "'a b'", "True"))
		self.assertEqual(py.values(test), [[1, 2], "a b", True])
		self.assertEqual(py.call("pick", test), "pick([1, 2], 'a b', True)")
		self.assertEqual(py.shown(["x"]), "['x']\n")

class TestViolations(Folders):
	"""python_violations(sources, allowed_imports, forbidden_calls): read in the source."""

	def test_imports_are_refused_unless_allowed(self):
		source = self.write("a.py", "import os\nfrom collections import deque\nimport math\n"
			"from typing import Any\n")
		self.assertEqual(python_violations([source], allowed_imports=("math",)),
			["import collections", "import os"])

	def test_forbidden_calls_as_names_or_methods(self):
		source = self.write("a.py", "def f(x):\n\tx.sort()\n\treturn sorted(x) + list(x)\n"
			"# sorted() in a comment does not count\ns = 'sorted()'\n")
		self.assertEqual(python_violations([source], forbidden_calls=("sorted", "sort")),
			["sort()", "sorted()"])

	def test_dunder_import_eval_and_exec_count_as_imports(self):
		source = self.write("a.py", "os = __import__('os')\nexec('import sys')\n")
		self.assertEqual(python_violations([source]), ["__import__()", "exec()"])

def double_oracle(params, test):
	return py.shown(2 * py.values(test)[0])

def double_tests(params, rng):
	return [py.case(0), py.case(21), py.case(-4)]

DOUBLE = make_exercise(
	name="double", language="python", kind="function", assignment_name="twice_${mode}",
	expected_files=("twice_${mode}.py",), allowed_functions=(),
	forbidden_calls=("sum",), subject="Return the double of n.",
	oracle=double_oracle, generate_tests=double_tests,
	harness=py.harness("twice_${mode}"), call=py.call, examples=(py.case(21),),
)

class TestGradePython(Folders):
	"""A whole grademe of a Python function, like a C one."""

	def grade(self, code):
		variant = Variant(DOUBLE, 0, {"mode": "common"})
		self.write("twice_common.py", code)
		return grade(variant, self.rendu, PythonRunner(PYTHON))

	def test_right_function_passes(self):
		result = self.grade("def twice_common(n):\n\treturn n * 2\n")
		self.assertTrue(result.passed, result.trace)
		self.assertEqual(result.tests_passed, 3)

	def test_wrong_function_fails_with_the_call_in_the_trace(self):
		result = self.grade("def twice_common(n):\n\treturn n + 2\n")
		self.assertFalse(result.passed)
		self.assertIn("$> twice_common(0)", result.trace)
		self.assertIn("-2$\n+0$", result.trace)

	def test_syntax_error_fails_at_compilation(self):
		result = self.grade("def twice_common(n)\n\treturn n * 2\n")
		self.assertFalse(result.passed)
		self.assertIn("python", result.trace)
		self.assertIn("SyntaxError", result.trace)

	def test_forbidden_call_fails_before_the_tests(self):
		result = self.grade("def twice_common(n):\n\treturn sum([n, n])\n")
		self.assertFalse(result.passed)
		self.assertIn("Forbidden: sum()", result.trace)
		self.assertEqual(result.tests_passed, 0)

class TestPythonSubject(unittest.TestCase):
	def test_header_and_examples_of_a_python_function(self):
		subject = render(Variant(DOUBLE, 0, {"mode": "common"}))
		lines = subject.splitlines()
		self.assertEqual(lines[:4], [
			"Assignment name  : twice_common",
			"Expected files   : twice_common.py",
			"Allowed imports  : none",
			"Forbidden        : sum()",
		])
		self.assertTrue(subject.endswith("Examples:\n\n>>> twice_common(21)\n42\n"), subject)

	def test_a_declaration_that_changes_with_the_variant(self):
		"""$prototype: given by prototype(name, params); unknown without it."""
		exo = make_exercise(subject="Declared as:\n\n$prototype",
			prototype=lambda name, params: f"def {name}(text: str) -> {params['mode']}:")
		self.assertIn("\ndef char_filter(text: str) -> common:\n", render(Variant(exo, 0, {"mode": "common"})))
		with self.assertRaises(ExerciseError):
			make_exercise(subject="Declared as: $prototype")

	def test_a_python_exercise_allows_no_c_function(self):
		with self.assertRaises(ExerciseError):
			make_exercise(language="python", allowed_functions=("write",))
