"""Tests of the caps_start and caps_end exercises (programs): oracles and variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

FOLDER = Path(__file__).resolve().parent.parent / "exercises/c"
START = run_path(str(FOLDER / "caps_start/exercise.py"))["EXERCISE"]
END = run_path(str(FOLDER / "caps_end/exercise.py"))["EXERCISE"]

def output(exercise, args, which, rest="lower"):
	return exercise.oracle({"which": which, "rest": rest}, TestCase(args))

class TestOracle(unittest.TestCase):
	def test_from_the_start_of_each_word(self):
		self.assertEqual(output(START, ("hELLO wORLD a",), "first_two"), "HEllo WOrld A\n")
		self.assertEqual(output(START, ("abc DEF x",), "second", "keep"), "aBc DEF x\n")
		self.assertEqual(output(START, ("hello WORLD sky",), "first_vowel"), "hEllo wOrld sky\n")

	def test_from_the_end_of_each_word(self):
		self.assertEqual(output(END, ("hello WORLD a",), "last_two"), "helLO worLD A\n")
		self.assertEqual(output(END, ("abc DEF x",), "second_last", "keep"), "aBc DEF x\n")
		self.assertEqual(output(END, ("hello WORLD queue",), "last_vowel"), "hellO wOrld queuE\n")

	def test_one_line_per_argument_and_none(self):
		self.assertEqual(output(START, ("ab", "cd"), "second"), "aB\ncD\n")
		self.assertEqual(output(END, (), "last_two"), "\n")

class TestVariants(unittest.TestCase):
	def test_six_variants_each_within_80_columns(self):
		for exercise in (START, END):
			combinations = exercise.combinations()
			self.assertEqual(len(combinations), 6)
			for params in combinations:
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
