"""Tests of the put_filter exercise (a void function that displays a string).

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/put_filter/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, what, end="bare"):
	return EXERCISE.oracle({"what": what, "end": end}, TestCase((text,)))

class TestOracle(unittest.TestCase):
	"""What ft_put_<what>_<end> displays, worked out by hand."""

	def test_each_filter(self):
		self.assertEqual(output("a1 B2!", "letters"), "aB")
		self.assertEqual(output("a1 B2!", "digits", "newline"), "12\n")
		self.assertEqual(output("Hi 42", "upper"), "HI 42")
		self.assertEqual(output("ab ", "doubled", "newline"), "aabb  \n")

	def test_nothing_to_display(self):
		self.assertEqual(output("", "doubled"), "")
		self.assertEqual(output("abc", "digits", "newline"), "\n")

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
