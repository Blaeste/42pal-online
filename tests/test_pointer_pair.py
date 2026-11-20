"""Tests of the pointer_pair exercise (a function on two ints through pointers).

The test main prints *a and *b after the call. The expected outputs below are
worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/pointer_pair/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(a, b, operation):
	return EXERCISE.oracle({"operation": operation}, TestCase((str(a), str(b))))

class TestOracle(unittest.TestCase):
	"""What *a and *b hold after ft_<operation>, worked out by hand."""

	def test_order(self):
		self.assertEqual(output(7, 3, "order_up"), "3 7\n")
		self.assertEqual(output(3, 7, "order_up"), "3 7\n")
		self.assertEqual(output(3, 7, "order_down"), "7 3\n")

	def test_sum_and_difference_of_the_old_values(self):
		"""7 and 3: a = 10, b = 4."""
		self.assertEqual(output(7, 3, "sum_diff"), "10 4\n")
		self.assertEqual(output(-2, 5, "sum_diff"), "3 -7\n")

	def test_swap_then_double_or_negate(self):
		self.assertEqual(output(7, 3, "swap_double"), "6 14\n")
		self.assertEqual(output(7, -3, "swap_negate"), "3 -7\n")

class TestVariants(unittest.TestCase):
	def test_five_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 5)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"{variant.name}(&a, &b) /* a = 7, b = 3 */", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
