"""Tests of the tab_index exercise (a function on an array of ints).

The test main builds the array from its arguments (NULL when there is none),
calls the function, then prints the index it returns. The expected outputs
below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/tab_index/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

# 3 -1 4 -1 5 9 2 6 5 3 5, indexes 0 to 10.
DIGITS_OF_PI = [3, -1, 4, -1, 5, 9, 2, 6, 5, 3, 5]

def output(numbers, which, rule):
	"""What the test main prints for ft_index_<which>_<rule> on `numbers`."""
	return EXERCISE.oracle({"which": which, "rule": rule}, TestCase(tuple(map(str, numbers))))

class TestOracle(unittest.TestCase):
	"""What ft_index_<which>_<rule> must return, worked out by hand."""

	def test_first_and_last_of_each_rule(self):
		"""9 is at 5; -1 at 1 and 3; 4 at 2, 6 at 7; repeated: 3, 8, 9 and 10."""
		for which, rule, index in [
			("first", "biggest", 5), ("last", "biggest", 5),
			("first", "smallest", 1), ("last", "smallest", 3),
			("first", "negative", 1), ("last", "negative", 3),
			("first", "even", 2), ("last", "even", 7),
			("first", "repeated", 3), ("last", "repeated", 10),
		]:
			self.assertEqual(output(DIGITS_OF_PI, which, rule), f"{index}\n", (which, rule))

	def test_the_same_value_everywhere(self):
		"""7 7 7: the biggest is at 0 first and at 2 last; the first repeated at 1."""
		self.assertEqual(output([7, 7, 7], "first", "biggest"), "0\n")
		self.assertEqual(output([7, 7, 7], "last", "smallest"), "2\n")
		self.assertEqual(output([7, 7, 7], "first", "repeated"), "1\n")

	def test_no_such_value_or_an_empty_array_gives_minus_1(self):
		"""1 3 5 has no even, negative or repeated value; no value at all: -1."""
		for rule in ["even", "negative", "repeated"]:
			self.assertEqual(output([1, 3, 5], "first", rule), "-1\n", rule)
		for rule in ["biggest", "smallest"]:
			self.assertEqual(output([], "last", rule), "-1\n", rule)

class TestVariants(unittest.TestCase):
	"""The variants of tab_index."""

	def test_ten_variants_with_compound_literals_within_80_columns(self):
		"""2 x 5; the calls are real C: (int[]){7, 7, 7} and NULL for no value."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 10)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"{variant.name}((int[]){{7, 7, 7}}, 3)", subject)
			self.assertIn(f"{variant.name}(NULL, 0)", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_an_empty_array_first(self):
		"""Same seed, same tests; NULL comes first, then one value."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertEqual(tests[:2], [TestCase(()), TestCase(("42",))])
