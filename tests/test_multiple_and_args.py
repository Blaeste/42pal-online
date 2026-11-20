"""Tests of the multiple_facts and arg_measure exercises (programs).

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
MULTIPLES = run_path(str(FOLDER / "multiple_facts/exercise.py"))["EXERCISE"]
ARGS = run_path(str(FOLDER / "arg_measure/exercise.py"))["EXERCISE"]

def multiples(args, what):
	return MULTIPLES.oracle({"what": what}, TestCase(args))

def measure(args, what):
	return ARGS.oracle({"what": what}, TestCase(args))

class TestMultiples(unittest.TestCase):
	def test_four_and_six(self):
		"""lcm 12; 1000 / 12 = 83; the first one over 100 is 108."""
		self.assertEqual(multiples(("4", "6"), "lcm_all"), "12\n")
		self.assertEqual(multiples(("4", "6"), "first_three"), "12 24 36\n")
		self.assertEqual(multiples(("4", "6"), "count_up_to_1000"), "83\n")
		self.assertEqual(multiples(("4", "6"), "next_after_100"), "108\n")

	def test_more_numbers_and_wrong_arguments(self):
		self.assertEqual(multiples(("2", "3", "4"), "lcm_all"), "12\n")
		self.assertEqual(multiples(("7", "11", "13"), "count_up_to_1000"), "0\n")
		self.assertEqual(multiples(("7", "11", "13"), "next_after_100"), "1001\n")
		for args in [(), ("4",), ("4", "0"), ("4", "x"), ("4", "1001"), ("1",) * 6]:
			self.assertEqual(multiples(args, "lcm_all"), "\n", args)

class TestArgs(unittest.TestCase):
	def test_each_measure(self):
		self.assertEqual(measure(("ab", "cde", ""), "total_length"), "5\n")
		self.assertEqual(measure(("ab", "cde", ""), "longest"), "3\n")
		self.assertEqual(measure(("12", "x1", "007", ""), "numbers"), "2\n")
		self.assertEqual(measure(("a", "b", "a", ""), "distinct"), "3\n")

	def test_no_argument_gives_0(self):
		for what in ["total_length", "longest", "numbers", "distinct"]:
			self.assertEqual(measure((), what), "0\n", what)

class TestVariants(unittest.TestCase):
	def test_four_variants_each_within_80_columns(self):
		for exercise in (MULTIPLES, ARGS):
			self.assertEqual(len(exercise.combinations()), 4)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
