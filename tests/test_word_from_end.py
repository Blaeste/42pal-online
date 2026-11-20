"""Tests of the word_from_end exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/word_from_end/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, which, how="plain"):
	return EXERCISE.oracle({"which": which, "how": how}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What from_end_<which>_<how> must print, worked out by hand."""

	def test_the_last_words(self):
		text = ("  one two\tthree  ",)
		self.assertEqual(output(text, "second_last"), "two\n")
		self.assertEqual(output(text, "last_two"), "two three\n")
		self.assertEqual(output(text, "last_two", "upper"), "TWO THREE\n")

	def test_the_last_capital_and_the_last_digit(self):
		self.assertEqual(output(("Hello world Foo bar",), "last_capital"), "Foo\n")
		self.assertEqual(output(("a1 b c2d e",), "last_digit", "upper"), "C2D\n")

	def test_no_such_word_gives_a_newline(self):
		self.assertEqual(output(("alone",), "second_last"), "\n")
		self.assertEqual(output(("alone",), "last_two"), "\n")
		self.assertEqual(output(("no capital here",), "last_capital"), "\n")
		for args in [(), ("a", "b"), ("",)]:
			self.assertEqual(output(args, "last_digit"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
