"""Tests of the alpha_wave exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/alpha_wave/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(wave, start, separator="joined", args=()):
	"""What alpha_wave_<wave>_<start>_<separator> prints."""
	params = {"wave": wave, "start": start, "separator": separator}
	return EXERCISE.oracle(params, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What alpha_wave_<wave>_<start>_<separator> must print, worked out by hand."""

	def test_waves_of_two_and_three_letters(self):
		"""ab CD ef GH...; A B C, then d e f in lowercase..."""
		self.assertEqual(output("2", "lower"), "abCDefGHijKLmnOPqrSTuvWXyz\n")
		self.assertEqual(output("3", "upper", "spaced"),
			"A B C d e f G H I j k l M N O p q r S T U v w x Y Z\n")

	def test_waves_of_one_starting_upper(self):
		"""AbCd...: the first letter in uppercase, then one out of two."""
		self.assertEqual(output("1", "upper"), "AbCdEfGhIjKlMnOpQrStUvWxYz\n")

	def test_the_arguments_are_ignored(self):
		self.assertEqual(output("2", "lower", args=("hello", "x")), "abCDefGHijKLmnOPqrSTuvWXyz\n")

class TestVariants(unittest.TestCase):
	"""The variants of alpha_wave."""

	def test_eleven_variants_without_the_real_subject(self):
		"""3 waves x 2 starts x 2 separators, without waves of 1, lowercase first, joined."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 11)
		self.assertNotIn({"wave": "1", "start": "lower", "separator": "joined"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
