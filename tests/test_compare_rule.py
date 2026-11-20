"""Tests of the compare_rule exercise (a function that compares two strings).

The test main prints the int returned. The expected outputs below are worked
out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/compare_rule/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(s1, s2, rule, result="difference"):
	return EXERCISE.oracle({"rule": rule, "result": result}, TestCase((s1, s2)))

class TestOracle(unittest.TestCase):
	"""What ft_compare_<rule>_<result> must return, worked out by hand."""

	def test_any_case(self):
		"""HELLO and hello are the same; Abc and abd: c - d = -1."""
		self.assertEqual(output("HELLO", "hello", "any_case"), "0\n")
		self.assertEqual(output("Abc", "ABD", "any_case"), "-1\n")

	def test_from_end(self):
		"""xab and yab differ at their first character: x - y = -1; ab against b: a - 0."""
		self.assertEqual(output("xab", "yab", "from_end"), "-1\n")
		self.assertEqual(output("ab", "b", "from_end"), "97\n")
		self.assertEqual(output("ab", "b", "from_end", "sign"), "1\n")

	def test_length_first(self):
		"""zz is shorter than aaa: 2 - 3 = -1; as long: like strcmp."""
		self.assertEqual(output("zz", "aaa", "length_first"), "-1\n")
		self.assertEqual(output("abc", "abd", "length_first", "sign"), "-1\n")

	def test_skip_spaces(self):
		"""a b c and abc are the same; ab and a c: b - c = -1."""
		self.assertEqual(output("a b\tc", "abc", "skip_spaces"), "0\n")
		self.assertEqual(output("ab", " a c", "skip_spaces"), "-1\n")

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
