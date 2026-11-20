"""Tests of the longest_span exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/longest_span/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, rule, tie="first"):
	"""What longest_<rule>_<tie> prints for these arguments."""
	return EXERCISE.oracle({"rule": rule, "tie": tie}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What longest_<rule>_<tie> must print, worked out by hand."""

	def test_no_character_twice(self):
		"""In pwwkew, wke starts at 2 and kew at 3."""
		self.assertEqual(output(("pwwkew",), "unique"), "wke\n")
		self.assertEqual(output(("pwwkew",), "unique", "last"), "kew\n")

	def test_parts_that_appear_twice_may_overlap(self):
		"""ana is at 1 and 3 in banana; in xyzxyabab, xy and ab both appear twice."""
		self.assertEqual(output(("banana",), "repeated"), "ana\n")
		self.assertEqual(output(("xyzxyabab",), "repeated"), "xy\n")
		self.assertEqual(output(("xyzxyabab",), "repeated", "last"), "ab\n")
		self.assertEqual(output(("abcd",), "repeated"), "\n")

	def test_sorted_parts_and_two_characters_at_most(self):
		"""dabcxyab: abcxy; acbd: ac then bd; aabbccdd: aabb, bbcc, ccdd."""
		self.assertEqual(output(("dabcxyab",), "sorted", "last"), "abcxy\n")
		self.assertEqual(output(("acbd",), "sorted", "last"), "bd\n")
		self.assertEqual(output(("eceba",), "two_chars"), "ece\n")
		self.assertEqual(output(("aabbccdd",), "two_chars"), "aabb\n")
		self.assertEqual(output(("aabbccdd",), "two_chars", "last"), "ccdd\n")

	def test_empty_or_not_one_argument_gives_a_newline(self):
		for args in [(), ("",), ("a", "b")]:
			self.assertEqual(output(args, "unique"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants of longest_span."""

	def test_eight_variants_within_80_columns(self):
		"""4 rules x 2 ties; the longest palindrome (a real subject) is not a rule."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible(self):
		"""Same seed, same tests; an empty string and one with spaces are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(("",)), tests)
		self.assertIn(TestCase(("to be or not to be",)), tests)
