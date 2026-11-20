"""Tests of the dup_shape exercise (a function returning a malloc'd string).

The test main prints the string returned, then a newline, and frees it.
The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/dup_shape/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, shape):
	return EXERCISE.oracle({"shape": shape}, TestCase((text,)))

class TestOracle(unittest.TestCase):
	def test_each_shape(self):
		self.assertEqual(output("abc", "reversed"), "cba\n")
		self.assertEqual(output("ab ", "doubled"), "aabb  \n")
		self.assertEqual(output("ab", "twice"), "abab\n")
		self.assertEqual(output(" \t a b \t", "trimmed"), "a b\n")
		self.assertEqual(output("Hi 42", "upper"), "HI 42\n")

	def test_an_empty_string_gives_an_empty_string(self):
		for shape in ["reversed", "doubled", "twice", "trimmed", "upper"]:
			self.assertEqual(output("", shape), "\n", shape)
		self.assertEqual(output("   ", "trimmed"), "\n")

class TestVariants(unittest.TestCase):
	def test_five_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 5)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
