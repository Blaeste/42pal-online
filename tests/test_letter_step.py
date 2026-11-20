"""Tests of the letter_step exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/letter_step/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, what, case="keep"):
	return EXERCISE.oracle({"what": what, "case": case}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What step_<what>_<case> must print, worked out by hand."""

	def test_vowels_and_consonants_move_to_the_next_one(self):
		"""e->i, o->u, u->a; b->c, z->b (the consonant after z is b)."""
		self.assertEqual(output(("Hello World",), "vowels"), "Hillu Wurld\n")
		self.assertEqual(output(("abz UZ",), "consonants"), "acb UB\n")

	def test_digits_and_letters_backwards(self):
		self.assertEqual(output(("a9b0",), "digits"), "a0b1\n")
		self.assertEqual(output(("Abc z",), "backward_letters"), "Zab y\n")

	def test_swap_changes_the_case_of_what_moves(self):
		"""A->Z then z; b->a then A; the space does not move."""
		self.assertEqual(output(("Abc z",), "backward_letters", "swap"), "zAB Y\n")
		self.assertEqual(output(("Hello",), "vowels", "swap"), "HIllU\n")

	def test_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b")]:
			self.assertEqual(output(args, "digits"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_seven_variants_within_80_columns(self):
		"""4 x 2, without digits with swap (digits have no case)."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 7)
		self.assertNotIn({"what": "digits", "case": "swap"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
