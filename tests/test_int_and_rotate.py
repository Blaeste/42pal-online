"""Tests of the int_to_text (a function) and word_rotate (a program) exercises.

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

FOLDER = Path(__file__).resolve().parent.parent / "exercises/c"
INT_TO_TEXT = run_path(str(FOLDER / "int_to_text/exercise.py"))["EXERCISE"]
ROTATE = run_path(str(FOLDER / "word_rotate/exercise.py"))["EXERCISE"]

def text(n, format):
	return INT_TO_TEXT.oracle({"format": format}, TestCase((str(n),)))

def rotate(args, move):
	return ROTATE.oracle({"move": move}, TestCase(args))

class TestIntToText(unittest.TestCase):
	def test_each_format(self):
		self.assertEqual(text(-1234567, "spaced"), "-1 234 567\n")
		self.assertEqual(text(1234567, "commas"), "1,234,567\n")
		self.assertEqual(text(42, "signed"), "+42\n")
		self.assertEqual(text(-42, "padded"), "-000042\n")
		self.assertEqual(text(1234567, "padded"), "1234567\n")

	def test_zero_and_the_ends_of_int(self):
		self.assertEqual(text(0, "signed"), "0\n")
		self.assertEqual(text(0, "padded"), "000000\n")
		self.assertEqual(text(-2147483648, "commas"), "-2,147,483,648\n")
		self.assertEqual(text(999, "spaced"), "999\n")

	def test_the_first_tests_hold_the_ends_of_int(self):
		tests = INT_TO_TEXT.generate_tests({"format": "spaced"}, Random(7))
		first = [test.args[0] for test in tests[:6]]
		for n in ["0", "-2147483648", "2147483647"]:
			self.assertIn(n, first)

class TestWordRotate(unittest.TestCase):
	def test_each_move(self):
		args = ("  one two\tthree four  ",)
		self.assertEqual(rotate(args, "swap_ends"), "four two three one\n")
		self.assertEqual(rotate(args, "first_two_last"), "three four one two\n")
		self.assertEqual(rotate(args, "longest_first"), "three one two four\n")
		self.assertEqual(rotate(args, "shortest_last"), "two three four one\n")

	def test_one_word_no_word_or_not_one_argument(self):
		self.assertEqual(rotate(("alone",), "swap_ends"), "alone\n")
		for args in [(), ("a", "b"), ("",), (" \t ",)]:
			self.assertEqual(rotate(args, "longest_first"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_four_variants_each_within_80_columns(self):
		for exercise in (INT_TO_TEXT, ROTATE):
			self.assertEqual(len(exercise.combinations()), 4)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
