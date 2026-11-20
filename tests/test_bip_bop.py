"""Tests of the bip_bop exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/bip_bop/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def lines(pair, upto):
	return EXERCISE.oracle({"pair": pair, "upto": upto}, TestCase(())).split("\n")

class TestOracle(unittest.TestCase):
	"""What bipbop_<pair>_<upto> must print, worked out by hand."""

	def test_multiples_of_3_and_4(self):
		"""3 bip, 4 bop, 12 both; 1, 2, 5 stay numbers."""
		out = lines("3_4", "30")
		self.assertEqual(out[:12], ["1", "2", "bip", "bop", "5", "bip", "7", "bop", "bip",
			"10", "11", "bipbop"])
		self.assertEqual(out[29], "bip")
		self.assertEqual(len(out), 31)
		self.assertEqual(out[30], "")

	def test_up_to_50_with_2_and_7(self):
		"""14, 28 and 42 are multiples of both; 49 of 7 only; 50 of 2."""
		out = lines("2_7", "50")
		self.assertEqual([out[13], out[27], out[41]], ["bipbop"] * 3)
		self.assertEqual(out[48:50], ["bop", "bip"])

class TestVariants(unittest.TestCase):
	def test_eight_variants_never_3_and_5(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		self.assertNotIn("3_5", EXERCISE.params[0].values)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
