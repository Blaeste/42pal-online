"""Tests of the word_order exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/word_order/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, order, separator="space"):
	"""What the program prints for these arguments and params."""
	return EXERCISE.oracle({"order": order, "separator": separator}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What <order>_words_<separator> must print, worked out by hand."""

	def test_reverse_and_rotations(self):
		"""Words are cut at spaces and tabs, then put in their new order."""
		self.assertEqual(output(("one two three",), "reverse", "comma"), "three, two, one\n")
		self.assertEqual(output(("  one two\tthree  ",), "rotate_left", "newline"), "two\nthree\none\n")
		self.assertEqual(output(("a b c d",), "rotate_right"), "d a b c\n")

	def test_sort_by_ascii_and_by_length(self):
		"""sort: ASCII order (A before b); by_length: shortest first, ties kept."""
		self.assertEqual(output(("pear Apple banana",), "sort"), "Apple banana pear\n")
		self.assertEqual(output(("ccc a bb dd",), "by_length"), "a bb dd ccc\n")

	def test_one_word_no_word_and_wrong_counts(self):
		"""One word stays as it is; no word, 0 or 2 arguments: a newline only."""
		self.assertEqual(output(("solo",), "rotate_right", "comma"), "solo\n")
		self.assertEqual(output((" \t ",), "sort"), "\n")
		for args in [(), ("a", "b")]:
			self.assertEqual(output(args, "by_length"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants of word_order."""

	def test_thirteen_variants_within_80_columns(self):
		"""5 orders x 3 separators, minus the two real subjects."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 13)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_the_edge_cases(self):
		"""Same seed, same tests; blanks only and a wrong count are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase((" \t ",)), tests)
		self.assertIn(TestCase(("two", "args")), tests)
