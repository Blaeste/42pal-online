"""Tests of the nest_report exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/nest_report/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, report, brackets):
	"""What nest_<report>_<brackets> prints for these arguments."""
	return EXERCISE.oracle({"report": report, "brackets": brackets}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What nest_<report>_<brackets> must print, worked out by hand."""

	def test_depth_or_error(self):
		"""(a(b)c): 2 open at most; {[()]}: 3; ([)]: wrong with three kinds, right with ()."""
		self.assertEqual(output(("(a(b)c)", "", "x"), "depth", "round"), "2\n0\n0\n")
		self.assertEqual(output(("{[()]}", "([)]"), "depth", "three"), "3\nError\n")
		self.assertEqual(output(("([)]",), "depth", "round"), "1\n")
		self.assertEqual(output(("(()", "())"), "depth", "round"), "Error\nError\n")

	def test_index_of_the_first_wrong_bracket(self):
		"""([)]: ) at 2 closes [; a): ) at 1 closes nothing; ((a: the ( at 1 stays open."""
		args = ("([)]", "a)", "((a", "{[]", "<ok>")
		self.assertEqual(output(args, "error_at", "three"), "2\n1\n1\n0\nOK\n")

	def test_completed_with_the_closing_brackets_missing(self):
		"""<{[(x gets )]}>; a(b gets ); (] is wrong; ok has nothing to close."""
		args = ("<{[(x", "a(b", "(]", "ok")
		self.assertEqual(output(args, "complete", "four"), "<{[(x)]}>\na(b)\nError\nok\n")

	def test_no_argument_gives_a_newline(self):
		self.assertEqual(output((), "complete", "round"), "\n")

class TestVariants(unittest.TestCase):
	"""The variants of nest_report."""

	def test_nine_variants_within_80_columns(self):
		"""3 reports x 3 sets of brackets; none says only OK or Error (a real subject)."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 9)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_several_strings_per_run(self):
		"""Same seed, same tests; no argument, and runs of several strings."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertEqual(tests[0], TestCase(()))
		self.assertTrue(any(len(test.args) > 2 for test in tests))
