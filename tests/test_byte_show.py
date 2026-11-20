"""Tests of the byte_show exercise (a void function that displays a byte).

The test main calls the function and prints nothing else. The expected
outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/byte_show/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(byte, form):
	return EXERCISE.oracle({"form": form}, TestCase((str(byte),)))

class TestOracle(unittest.TestCase):
	"""What ft_show_<form>(38) displays: 38 is 00100110, 0x26, 046."""

	def test_each_form_of_38(self):
		self.assertEqual(output(38, "lsb_first"), "01100100")
		self.assertEqual(output(38, "grouped"), "0010 0110")
		self.assertEqual(output(38, "dots"), "..#..##.")
		self.assertEqual(output(38, "hex"), "26")
		self.assertEqual(output(38, "octal"), "046")

	def test_the_ends(self):
		self.assertEqual(output(0, "hex"), "00")
		self.assertEqual(output(255, "octal"), "377")
		self.assertEqual(output(1, "lsb_first"), "10000000")

class TestVariants(unittest.TestCase):
	def test_five_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 5)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
