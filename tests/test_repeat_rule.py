"""Tests of the repeat_rule exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/repeat_rule/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, rule):
	return EXERCISE.oracle({"rule": rule}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What repeat_by_<rule> must print, worked out by hand."""

	def test_reverse_rank_and_vowel_rank(self):
		"""z once, y twice, A 26 times; e twice, o 4 times."""
		self.assertEqual(output(("zyA",), "reverse_rank"), "zyy" + "A" * 26 + "\n")
		self.assertEqual(output(("Hello",), "vowel_rank"), "Heelloooo\n")

	def test_digit_value(self):
		"""3 three times, 0 not at all, 1 once."""
		self.assertEqual(output(("a3b0c1",), "digit_value"), "a333bc1\n")

	def test_position_and_word_number(self):
		"""a b: the space second, b third; the third word all: each letter 3 times."""
		self.assertEqual(output(("a b",), "position"), "a  bbb\n")
		self.assertEqual(output(("hi you  all",), "word_number"), "hi yyoouu  aaallllll\n")

	def test_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b")]:
			self.assertEqual(output(args, "position"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_five_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 5)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
