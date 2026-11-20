"""Tests of the replace_pick exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/replace_pick/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, which, match="exact"):
	return EXERCISE.oracle({"which": which, "match": match}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What replace_<which>_<match> must print, worked out by hand."""

	def test_which_occurrences_of_a_in_banana(self):
		"""The a of banana are at 1, 3 and 5."""
		args = ("banana", "a", "o")
		self.assertEqual(output(args, "first"), "bonana\n")
		self.assertEqual(output(args, "last"), "banano\n")
		self.assertEqual(output(args, "every_other"), "bonano\n")
		self.assertEqual(output(args, "all_but_first"), "banono\n")

	def test_any_case_finds_both_cases(self):
		self.assertEqual(output(("Abba", "a", "x"), "first", "any_case"), "xbba\n")
		self.assertEqual(output(("Abba", "a", "x"), "first"), "Abbx\n")
		self.assertEqual(output(("Abba", "A", "-"), "last", "any_case"), "Abb-\n")

	def test_wrong_arguments_or_nothing_found(self):
		for args in [("abc",), ("abc", "ab", "x"), ("abc", "a", ""), ("a", "b", "c", "d")]:
			self.assertEqual(output(args, "first"), "\n", args)
		self.assertEqual(output(("abc", "z", "x"), "last"), "abc\n")

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
