"""Tests of the print_range exercise (a void function that prints).

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/print_range/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(chars, order="up", step="all"):
	"""What the function prints, for these params (it takes no argument)."""
	return EXERCISE.oracle({"chars": chars, "order": order, "step": step}, TestCase())

class TestOracle(unittest.TestCase):
	"""What ft_print_<chars>_<order>_<step> must print, worked out by hand."""

	def test_every_character_up_or_down_with_no_newline(self):
		"""The whole range, in one order or the other, and nothing after it."""
		self.assertEqual(output("lowercase"), "abcdefghijklmnopqrstuvwxyz")
		self.assertEqual(output("uppercase", order="down"), "ZYXWVUTSRQPONMLKJIHGFEDCBA")

	def test_skip_takes_one_out_of_two_from_the_first(self):
		"""skip: the 1st, 3rd, 5th... of the range, in its order."""
		self.assertEqual(output("digits", step="skip"), "02468")
		self.assertEqual(output("digits", order="down", step="skip"), "97531")
		self.assertEqual(output("lowercase", order="down", step="skip"), "zxvtrpnljhfdb")

class TestVariants(unittest.TestCase):
	"""The variants of print_range."""

	def test_ten_variants_without_the_real_subjects(self):
		"""3 ranges x 2 orders x 2 steps, minus all the digits up or down."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 10)
		self.assertNotIn({"chars": "digits", "order": "up", "step": "all"}, combinations)
		self.assertNotIn({"chars": "digits", "order": "down", "step": "all"}, combinations)

	def test_the_example_shows_the_output_with_no_newline(self):
		"""ft_print_digits_up_skip() then 02468, without a $ at the end."""
		subject = render(Variant(EXERCISE, 0, {"chars": "digits", "order": "up", "step": "skip"}))
		self.assertIn("void\tft_print_digits_up_skip(void);", subject)
		self.assertTrue(subject.endswith("ft_print_digits_up_skip()\n02468\n"), subject)
		for line in subject.splitlines():
			self.assertLessEqual(len(line), 80, line)
