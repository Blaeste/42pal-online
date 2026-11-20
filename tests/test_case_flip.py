"""Tests of the case_flip exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/case_flip/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, action, letters):
	"""What <action>_<letters> prints for these arguments."""
	return EXERCISE.oracle({"action": action, "letters": letters}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What <action>_<letters> must print, worked out by hand."""

	def test_vowels_and_consonants(self):
		"""Only a, e, i, o, u (and their capitals) are vowels; y is a consonant."""
		self.assertEqual(output(("Hello World",), "swap", "vowels"), "HEllO WOrld\n")
		self.assertEqual(output(("Hello World",), "upper", "consonants"), "HeLLo WoRLD\n")
		self.assertEqual(output(("YES you",), "lower", "consonants"), "yEs you\n")

	def test_one_letter_out_of_two_counting_letters_only(self):
		"""In a-b c!d, the letters are a b c d: the 1st and the 3rd change."""
		self.assertEqual(output(("a-b c!d",), "upper", "every_other"), "A-b C!d\n")
		self.assertEqual(output(("ABCD",), "swap", "every_other"), "aBcD\n")

	def test_the_first_letter_of_each_word(self):
		"""Words are cut by spaces and tabs; 42abc starts with a digit."""
		self.assertEqual(output(("  hello  wORLD\tx 42abc",), "swap", "word_starts"),
			"  Hello  WORLD\tX 42abc\n")

	def test_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b")]:
			self.assertEqual(output(args, "lower", "vowels"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants of case_flip."""

	def test_twelve_variants_within_80_columns(self):
		"""3 actions x 4 sets of letters; none swaps every letter (a real subject)."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 12)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible(self):
		params = EXERCISE.combinations()[0]
		self.assertEqual(EXERCISE.generate_tests(params, Random(7)),
			EXERCISE.generate_tests(params, Random(7)))
