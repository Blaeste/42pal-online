"""Tests of the tab_sort exercise (a function that sorts an array of ints in place).

The test main builds the array from its arguments (NULL when there is none),
calls the function, then prints the array. The expected outputs below are
worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/tab_sort/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(numbers, key, order="up"):
	"""What the test main prints after ft_sort_by_<key>_<order> on `numbers`."""
	return EXERCISE.oracle({"key": key, "order": order}, TestCase(tuple(map(str, numbers))))

class TestOracle(unittest.TestCase):
	"""The array after ft_sort_by_<key>_<order>, worked out by hand."""

	def test_absolute_value_with_the_negative_one_first(self):
		"""|3 -1 4 -3 0 -5| = 3 1 4 3 0 5: 0 -1 -3 3 4 -5; down is the reverse."""
		self.assertEqual(output([3, -1, 4, -3, 0, -5], "absolute"), "0 -1 -3 3 4 -5\n")
		self.assertEqual(output([3, -1, 4, -3, 0, -5], "absolute", "down"), "-5 4 3 -3 -1 0\n")

	def test_even_numbers_first_then_odd_ones(self):
		"""Evens -4 0 2 8, then odds -3 5 7."""
		numbers = [5, 2, -3, 8, 0, 7, -4]
		self.assertEqual(output(numbers, "parity"), "-4 0 2 8 -3 5 7\n")
		self.assertEqual(output(numbers, "parity", "down"), "7 5 -3 8 2 0 -4\n")

	def test_last_digit_then_number_of_digits(self):
		"""Last digits 1 3 0 1 5 3; numbers of digits 3 1 2 1 2 1."""
		self.assertEqual(output([21, 13, 40, -11, 5, 33], "last_digit"), "40 -11 21 13 33 5\n")
		self.assertEqual(output([100, -7, 42, 0, -55, 3], "digit_count"), "-7 0 3 -55 42 100\n")

	def test_no_value_or_one(self):
		"""An empty array prints an empty line; one value stays."""
		self.assertEqual(output([], "parity"), "\n")
		self.assertEqual(output([5], "absolute", "down"), "5\n")

class TestVariants(unittest.TestCase):
	"""The variants of tab_sort."""

	def test_eight_variants_within_80_columns(self):
		"""4 keys x 2 orders; no key sorts by value alone (a real subject)."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"{variant.name}((int[]){{3, -1, 4, -3, 0, -5}}, 6)", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_an_empty_array(self):
		"""Same seed, same tests; NULL and a reversed array are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(()), tests)
		self.assertIn(TestCase(tuple("9876543210")), tests)
