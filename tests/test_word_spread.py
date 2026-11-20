"""Tests of the word_spread exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/word_spread/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, gap, ends="inside"):
	return EXERCISE.oracle({"gap": gap, "ends": ends}, TestCase(args))

class TestOracle(unittest.TestCase):
	def test_gaps_and_ends(self):
		text = ("  a  bc d ",)
		self.assertEqual(output(text, "2"), "a  bc  d\n")
		self.assertEqual(output(text, "tab", "around"), "\ta\tbc\td\t\n")
		self.assertEqual(output(text, "4", "around"), "    a    bc    d    \n")

	def test_no_word_or_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b"), ("",), ("   ",)]:
			self.assertEqual(output(args, "2", "around"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_six_variants_never_three_spaces(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 6)
		self.assertNotIn("3", EXERCISE.params[0].values)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
