"""Tests of the alpha_back exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/alpha_back/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(pattern, step="all"):
	"""What alpha_back_<pattern>_<step> prints."""
	return EXERCISE.oracle({"pattern": pattern, "step": step}, TestCase(()))

class TestOracle(unittest.TestCase):
	"""What alpha_back_<pattern>_<step> must print, worked out by hand."""

	def test_every_letter_from_z_to_a(self):
		"""ZyXw...; Zyx Wvu, one in three; z to n in uppercase, then lowercase."""
		self.assertEqual(output("alternate_upper"), "ZyXwVuTsRqPoNmLkJiHgFeDcBa\n")
		self.assertEqual(output("thirds"), "ZyxWvuTsrQpoNmlKjiHgfEdcBa\n")
		self.assertEqual(output("halves"), "ZYXWVUTSRQPONmlkjihgfedcba\n")

	def test_one_letter_out_of_two(self):
		"""z x v t r p n l j h f d b, the case counted on the letters shown."""
		self.assertEqual(output("alternate_lower", "skip"), "zXvTrPnLjHfDb\n")
		self.assertEqual(output("halves", "skip"), "ZXVTRPNljhfdb\n")

class TestVariants(unittest.TestCase):
	"""The variants of alpha_back."""

	def test_seven_variants_without_the_real_subject(self):
		"""4 patterns x 2 steps, without zYxW... for every letter."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 7)
		self.assertNotIn({"pattern": "alternate_lower", "step": "all"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
