"""Tests of the base_print exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/base_print/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, base, form="plain"):
	"""What to_<base>_<form> prints for these arguments."""
	return EXERCISE.oracle({"base": base, "form": form}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What to_<base>_<form> must print, worked out by hand."""

	def test_each_base_and_form(self):
		"""10 = 1010 in binary; 8 = 10 in octal; 255 = ff in hexadecimal."""
		self.assertEqual(output(("10",), "binary"), "1010\n")
		self.assertEqual(output(("8",), "octal", "prefixed"), "0o10\n")
		self.assertEqual(output(("255",), "hex", "prefixed"), "0xff\n")
		self.assertEqual(output(("007",), "binary"), "111\n")

	def test_groups_of_four_digits_from_the_right(self):
		"""256 = 1 0000 0000; 0x123456 = 1193046."""
		self.assertEqual(output(("255",), "binary", "grouped"), "1111 1111\n")
		self.assertEqual(output(("256",), "binary", "grouped"), "1 0000 0000\n")
		self.assertEqual(output(("1193046",), "hex", "grouped"), "12 3456\n")
		self.assertEqual(output(("2147483647",), "binary", "grouped"),
			"111 1111 1111 1111 1111 1111 1111 1111\n")

	def test_zero_and_not_one_argument(self):
		"""0 is 0 in every base; no argument or two give a newline."""
		self.assertEqual(output(("0",), "binary", "prefixed"), "0b0\n")
		self.assertEqual(output(("0",), "hex", "grouped"), "0\n")
		self.assertEqual(output((), "octal"), "\n")
		self.assertEqual(output(("1", "2"), "octal"), "\n")

class TestVariants(unittest.TestCase):
	"""The variants of base_print."""

	def test_eight_variants_without_print_hex_within_80_columns(self):
		"""3 bases x 3 forms, without hexadecimal as it is."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 8)
		self.assertNotIn({"base": "hex", "form": "plain"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_the_edges(self):
		"""Same seed, same tests; 0 and the biggest int are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		for number in ["0", "2147483647"]:
			self.assertIn(TestCase((number,)), tests)
