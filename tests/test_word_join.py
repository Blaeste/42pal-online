"""Tests of the word_join exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/word_join/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, joint, case="keep"):
	return EXERCISE.oracle({"joint": joint, "case": case}, TestCase(args))

class TestOracle(unittest.TestCase):
	def test_each_joint(self):
		text = ("  Hello   big\tWorld  ",)
		self.assertEqual(output(text, "dash"), "Hello-big-World\n")
		self.assertEqual(output(text, "comma", "lower"), "hello, big, world\n")
		self.assertEqual(output(text, "newline"), "Hello\nbig\nWorld\n")
		self.assertEqual(output(text, "dot", "lower"), "hello.big.world\n")

	def test_no_word_or_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b"), ("",), (" \t ",)]:
			self.assertEqual(output(args, "dash"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_eight_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
