"""Tests of the read_int exercise (a function that reads an int in base 10).

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/read_int/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, start, signs):
	return EXERCISE.oracle({"start": start, "signs": signs}, TestCase((text,)))

class TestOracle(unittest.TestCase):
	"""What ft_read_int_<start>_<signs> must return, worked out by hand."""

	def test_the_number_must_start_at_once(self):
		self.assertEqual(output("42abc", "nothing", "one"), "42\n")
		self.assertEqual(output(" 42", "nothing", "one"), "0\n")
		self.assertEqual(output("--5", "nothing", "one"), "0\n")
		self.assertEqual(output("+-3", "nothing", "many"), "-3\n")

	def test_spaces_and_a_minus_only(self):
		self.assertEqual(output("  \t-12x", "spaces", "minus_only"), "-12\n")
		self.assertEqual(output(" +12", "spaces", "minus_only"), "0\n")

	def test_anything_before_the_first_number(self):
		"""a+-5: the + is not followed by a digit, the - is; x+-+-7: two minus, +7."""
		self.assertEqual(output("abc-12def", "anything", "one"), "-12\n")
		self.assertEqual(output("a+-5", "anything", "one"), "-5\n")
		self.assertEqual(output("x+-+-7", "anything", "many"), "7\n")
		self.assertEqual(output("-+-+-3", "anything", "many"), "-3\n")
		self.assertEqual(output("a+5", "anything", "minus_only"), "5\n")
		self.assertEqual(output("no digit", "anything", "one"), "0\n")

class TestVariants(unittest.TestCase):
	def test_seven_variants_without_the_atoi_ones(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 7)
		for real in [{"start": "spaces", "signs": "one"}, {"start": "spaces", "signs": "many"}]:
			self.assertNotIn(real, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
