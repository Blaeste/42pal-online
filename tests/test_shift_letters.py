"""Tests of the shift_letters exercise: its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle:
that is what checks the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

# run_path runs exercise.py and returns its global names, EXERCISE among them.
EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/shift_letters/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, shift, direction="forward", letters="all"):
	"""What the oracle says the program prints for these arguments and params."""
	params = {"shift": shift, "direction": direction, "letters": letters}
	return EXERCISE.oracle(params, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What shift_letters must print, worked out by hand."""

	def test_forward_shift_of_every_letter(self):
		"""Each letter moves forward, z wraps to a; other characters stay."""
		# a b c +2 = c d e; x y z +2 = z a b (wrapping after z).
		self.assertEqual(output(("abc xyz",), "2"), "cde zab\n")
		# Case is kept: H+2 = J, W+2 = Y; the comma, space and ! stay.
		self.assertEqual(output(("Hello, World!",), "2"), "Jgnnq, Yqtnf!\n")

	def test_backward_shift(self):
		"""backward: each letter moves back, a wraps to z."""
		# a b c -3 = x y z (wrapping before a); x y z -3 = u v w.
		self.assertEqual(output(("abc xyz",), "3", direction="backward"), "xyz uvw\n")
		# H-3 = E, e-3 = b, l-3 = i, o-3 = l, W-3 = T, r-3 = o, d-3 = a.
		self.assertEqual(output(("Hello, World!",), "3", direction="backward"), "Ebiil, Tloia!\n")

	def test_only_one_case_of_letters_moves(self):
		"""lowercase or uppercase: the other letters stay as they are."""
		# Lowercase +5: e = j, l = q, o = t, r = w, d = i; H and W stay.
		self.assertEqual(output(("Hello, World!",), "5", letters="lowercase"), "Hjqqt, Wtwqi!\n")
		# Uppercase -2: H = F, W = U; every lowercase letter stays.
		self.assertEqual(
			output(("Hello, World!",), "2", direction="backward", letters="uppercase"),
			"Fello, Uorld!\n",
		)

	def test_wrong_number_of_arguments_prints_only_a_newline(self):
		"""With 0 or 2 arguments, every variant prints only a newline."""
		for args in [(), ("abc", "def")]:
			self.assertEqual(output(args, "3", direction="backward"), "\n", args)
		# One empty string is the right number of arguments: an empty line.
		self.assertEqual(output(("",), "3"), "\n")

class TestVariants(unittest.TestCase):
	"""The variants that can be drawn from shift_letters."""

	def test_generated_tests_are_reproducible_and_cover_edge_cases(self):
		"""Same seed, same tests; wrong counts and the ends of the alphabet are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertTrue(any(len(test.args) != 1 for test in tests), "no test with a wrong number of arguments")
		self.assertIn(TestCase(("az AZ",)), tests)
		self.assertGreaterEqual(len(tests), 10)

	def test_every_variant_has_a_subject_within_80_columns(self):
		"""3 shifts x 2 directions x 3 letter sets: 18 subjects, lines of 80 at most."""
		self.assertEqual(len(EXERCISE.combinations()), 18)
		for params in EXERCISE.combinations():
			subject = render(Variant(EXERCISE, 0, params))
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
