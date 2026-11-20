"""Tests of the word_pick exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/word_pick/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, which, how="plain"):
	"""What <which>_word_<how> prints for these arguments."""
	return EXERCISE.oracle({"which": which, "how": how}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What <which>_word_<how> must print, worked out by hand."""

	def test_which_word_spaces_and_tabs_around(self):
		"""In "  lorem\\tipsum  dolor ": lorem, ipsum, dolor."""
		text = ("  lorem\tipsum  dolor ",)
		self.assertEqual(output(text, "first", "upper"), "LOREM\n")
		self.assertEqual(output(text, "second"), "ipsum\n")
		self.assertEqual(output(text, "last", "reversed"), "rolod\n")

	def test_longest_is_the_first_of_the_longest(self):
		"""a bb ccc dd: ccc; Tie tie abc: Tie, the first of three."""
		self.assertEqual(output(("a bb ccc dd e",), "longest"), "ccc\n")
		self.assertEqual(output(("Tie tie abc",), "longest", "reversed"), "eiT\n")

	def test_upper_changes_lowercase_letters_only(self):
		"""Digits, signs and capitals stay as they are."""
		self.assertEqual(output(("x2-Go! now",), "first", "upper"), "X2-GO!\n")

	def test_no_such_word_gives_a_newline(self):
		"""No argument, two, an empty or blank string, or one word for second."""
		for args in [(), ("a", "b"), ("",), (" \t ",)]:
			self.assertEqual(output(args, "longest"), "\n", args)
		self.assertEqual(output(("alone",), "second"), "\n")

class TestVariants(unittest.TestCase):
	"""The variants of word_pick."""

	def test_ten_variants_without_first_word_and_last_word(self):
		"""4 x 3, without the first and the last word as they are; 80 columns."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 10)
		names = set()
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			names.add(variant.name)
			for line in render(variant).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
		self.assertNotIn("first_word_plain", names)
		self.assertIn("second_word_plain", names)

	def test_generated_tests_are_reproducible_with_blank_strings(self):
		"""Same seed, same tests; empty and blank strings are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(("",)), tests)
		self.assertIn(TestCase((" \t ",)), tests)
