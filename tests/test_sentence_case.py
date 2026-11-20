"""Tests of the sentence_case exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/sentence_case/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, style):
	return EXERCISE.oracle({"style": style}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What sentence_to_<style> must print, worked out by hand."""

	def test_each_style(self):
		"""Hello, big WORLD 42!: the words hello big world 42."""
		text = ("Hello, big WORLD 42!",)
		self.assertEqual(output(text, "camel"), "helloBigWorld42\n")
		self.assertEqual(output(text, "pascal"), "HelloBigWorld42\n")
		self.assertEqual(output(text, "snake"), "hello_big_world_42\n")
		self.assertEqual(output(text, "kebab"), "hello-big-world-42\n")
		self.assertEqual(output(text, "constant"), "HELLO_BIG_WORLD_42\n")
		self.assertEqual(output(text, "dot"), "hello.big.world.42\n")

	def test_no_word_or_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b"), ("",), (" -!- ",)]:
			self.assertEqual(output(args, "camel"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_six_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 6)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
