"""Tests of the arg_pick exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/arg_pick/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, which, case="as_is"):
	"""What the program prints for these arguments and params."""
	return EXERCISE.oracle({"which": which, "case": case}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What print_<which>_<case> must print, worked out by hand."""

	def test_first_and_last_in_upper_case(self):
		"""upper: each lowercase letter becomes uppercase; the rest stays."""
		self.assertEqual(output(("hello", "world"), "first", "upper"), "HELLO\n")
		self.assertEqual(output(("hello", "42 rue"), "last", "upper"), "42 RUE\n")

	def test_longest_and_shortest_keep_the_first_on_a_tie(self):
		"""Two of the same length: the first one is printed."""
		self.assertEqual(output(("a", "ccc", "bb"), "longest"), "ccc\n")
		self.assertEqual(output(("ab", "cd", "e"), "longest"), "ab\n")
		self.assertEqual(output(("ccc", "a", "bb"), "shortest"), "a\n")
		self.assertEqual(output(("ab", "cd", "efg"), "shortest"), "ab\n")
		# An empty argument is the shortest of all: only the newline.
		self.assertEqual(output(("x", ""), "shortest"), "\n")
		self.assertEqual(output(("Hello", "Hi!"), "shortest", "upper"), "HI!\n")

	def test_no_argument_prints_only_a_newline(self):
		"""Nothing to pick: a newline, whatever the variant."""
		for which in ["first", "last", "longest", "shortest"]:
			self.assertEqual(output((), which, "upper"), "\n", which)

class TestVariants(unittest.TestCase):
	"""The variants of arg_pick."""

	def test_six_variants_without_the_real_subjects(self):
		"""4 x 2 minus first and last as they are; subjects within 80 columns."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 6)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_ties_and_no_argument(self):
		"""Same seed, same tests; no argument and equal lengths are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(()), tests)
		self.assertIn(TestCase(("same", "size", "four")), tests)
