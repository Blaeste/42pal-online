"""Tests of the bit_check exercise (a function on the bits of an unsigned int).

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/bit_check/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def answers(property, numbers):
	"""The answers of ft_is_<property> for each number, as a string of 0 and 1."""
	return "".join(EXERCISE.oracle({"property": property}, TestCase((str(n),))).strip()
		for n in numbers)

class TestOracle(unittest.TestCase):
	"""What ft_is_<property> must return, worked out by hand."""

	def test_each_property(self):
		numbers = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 16]
		self.assertEqual(answers("power_of_4", numbers), "01001000001")
		self.assertEqual(answers("all_ones", numbers), "01010001000")
		self.assertEqual(answers("alternating", numbers), "01100100010")
		self.assertEqual(answers("bit_palindrome", numbers), "01010101100")
		self.assertEqual(answers("two_ones", numbers), "00010110110")

	def test_the_biggest_unsigned_ints(self):
		"""4294967295 is 32 ones; 0xAAAAAAAA alternates; 2^31 is a power of 2 but not of 4."""
		self.assertEqual(answers("all_ones", [4294967295]), "1")
		self.assertEqual(answers("alternating", [2863311530, 1431655765]), "11")
		self.assertEqual(answers("power_of_4", [2147483648, 1073741824]), "01")

class TestVariants(unittest.TestCase):
	def test_five_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 5)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
