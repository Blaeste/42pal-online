"""Tests of the calc_form exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/calc_form/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, order, operators="symbols", show="result"):
	"""What calc_<order>_<operators>_<show> prints for these arguments."""
	params = {"order": order, "operators": operators, "show": show}
	return EXERCISE.oracle(params, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What calc_<order>_<operators>_<show> must print, worked out by hand."""

	def test_the_three_orders(self):
		"""+ 7 3, 7 3 *, and 7 minus 10 in words."""
		self.assertEqual(output(("+", "7", "3"), "prefix"), "10\n")
		self.assertEqual(output(("7", "3", "*"), "postfix"), "21\n")
		self.assertEqual(output(("7", "minus", "10"), "infix", "words"), "-3\n")

	def test_division_and_remainder_go_toward_zero(self):
		"""-7 / 2 = -3 and -7 % 2 = -1, like in C."""
		self.assertEqual(output(("/", "-7", "2"), "prefix"), "-3\n")
		self.assertEqual(output(("-7", "2", "mod"), "postfix", "words"), "-1\n")

	def test_the_equation_is_written_infix(self):
		"""Whatever the order given: 7 over 2 = 3; 12 % 5 = 2."""
		self.assertEqual(output(("over", "7", "2"), "prefix", "words", "equation"),
			"7 over 2 = 3\n")
		self.assertEqual(output(("12", "%", "5"), "infix", "symbols", "equation"), "12 % 5 = 2\n")

	def test_not_three_arguments_gives_a_newline(self):
		for args in [(), ("1", "+"), ("1", "+", "2", "3")]:
			self.assertEqual(output(args, "infix", "words"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants of calc_form."""

	def test_eleven_variants_without_the_real_subject(self):
		"""3 orders x 2 sets of operators x 2 displays, without infix, symbols, result."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 11)
		self.assertNotIn({"order": "infix", "operators": "symbols", "show": "result"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_and_in_the_variant_form(self):
		"""Same seed, same tests; in prefix, the operator comes first."""
		params = {"order": "prefix", "operators": "words", "show": "result"}
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		for test in tests:
			if len(test.args) == 3:
				self.assertIn(test.args[0], ["plus", "minus", "times", "over", "mod"])
