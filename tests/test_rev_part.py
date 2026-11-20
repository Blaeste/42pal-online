"""Tests of the rev_part exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/rev_part/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, part):
	return EXERCISE.oracle({"part": part}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What rev_<part> must print, worked out by hand."""

	def test_words_and_letters(self):
		"""Each word turned around in place; the letters turned, the rest kept."""
		self.assertEqual(output(("  hello  big world ",), "each_word"), "  olleh  gib dlrow \n")
		self.assertEqual(output(("a-bc!d",), "letters_only"), "d-cb!a\n")

	def test_halves_and_pairs(self):
		"""abcdefg: the middle g stays with the second half; pairs ab cd ef, g alone."""
		self.assertEqual(output(("abcdef",), "halves"), "defabc\n")
		self.assertEqual(output(("abcdefg",), "halves"), "defgabc\n")
		self.assertEqual(output(("abcdefg",), "pairs"), "badcfeg\n")

	def test_even_places_only(self):
		"""abcdefg: a c e g at places 0 2 4 6 become g e c a."""
		self.assertEqual(output(("abcdefg",), "odd_places"), "gbedcfa\n")

	def test_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b")]:
			self.assertEqual(output(args, "pairs"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_five_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 5)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
