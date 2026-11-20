"""Tests of the merge_chars exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/merge_chars/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, which, order="appearance"):
	return EXERCISE.oracle({"which": which, "order": order}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What merge_<which>_<order> must print, worked out by hand."""

	def test_hello_world(self):
		"""Both: d e h l o r w; once: h e (hello only), w r d (world only)."""
		self.assertEqual(output(("hello", "world"), "all", "ascii"), "dehlorw\n")
		self.assertEqual(output(("hello", "world"), "once"), "hewrd\n")
		self.assertEqual(output(("hello", "world"), "once", "reverse_ascii"), "wrhed\n")

	def test_letters_only(self):
		self.assertEqual(output(("ab1", "BA2!"), "letters", "reverse_ascii"), "baBA\n")
		self.assertEqual(output(("a-a", "--"), "letters"), "a\n")

	def test_not_two_arguments_gives_a_newline(self):
		for args in [(), ("a",), ("a", "b", "c")]:
			self.assertEqual(output(args, "once"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_eight_variants_without_the_real_subject(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		self.assertNotIn({"which": "all", "order": "appearance"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
