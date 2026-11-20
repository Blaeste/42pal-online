"""Tests of the copy_shape exercise (a function that copies a string into a buffer).

The test main fills dst with X, calls the function, then prints dst and where
the pointer returned is in it. The expected outputs below are worked out by
hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/copy_shape/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(src, what, returned="start"):
	return EXERCISE.oracle({"what": what, "returned": returned}, TestCase((src,)))

class TestOracle(unittest.TestCase):
	"""What dst holds and where the pointer returned is, worked out by hand."""

	def test_each_shape_returning_the_start(self):
		self.assertEqual(output("hello", "reversed"), "dst: olleh\nreturned: dst + 0\n")
		self.assertEqual(output("Hi 42", "upper"), "dst: HI 42\nreturned: dst + 0\n")

	def test_returning_the_end_points_to_the_nul_written(self):
		"""a1b2 c keeps abc, 3 characters: the \\0 is at dst + 3."""
		self.assertEqual(output("a1b2 c", "letters", "end"), "dst: abc\nreturned: dst + 3\n")
		self.assertEqual(output(" a b ", "no_spaces", "end"), "dst: ab\nreturned: dst + 2\n")
		self.assertEqual(output("", "reversed", "end"), "dst: \nreturned: dst + 0\n")

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
