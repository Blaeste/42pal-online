"""Tests of the span_set exercise (a function measuring a run of characters).

The test main prints the size returned. The expected outputs below are
worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/span_set/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, set, side):
	return EXERCISE.oracle({"set": set, "side": side}, TestCase((text,)))

class TestOracle(unittest.TestCase):
	def test_each_set_and_side(self):
		self.assertEqual(output("123abc45", "digits", "start"), "3\n")
		self.assertEqual(output("123abc45", "digits", "end"), "2\n")
		self.assertEqual(output("abC12", "letters", "start"), "3\n")
		self.assertEqual(output("ab \t ", "blanks", "end"), "3\n")
		self.assertEqual(output("aEiXy", "vowels", "start"), "3\n")

	def test_no_such_run_or_an_empty_string(self):
		self.assertEqual(output("x12", "digits", "start"), "0\n")
		self.assertEqual(output("", "vowels", "end"), "0\n")
		self.assertEqual(output("2024", "digits", "end"), "4\n")

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
