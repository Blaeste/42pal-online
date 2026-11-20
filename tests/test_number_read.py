"""Tests of the number_read exercise (a function that reads a number).

The test main prints the int the function returns. The expected outputs
below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/number_read/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, base, format="plain"):
	"""What the test main prints for ft_read_<base>_<format>(text)."""
	return EXERCISE.oracle({"base": base, "format": format}, TestCase((text,)))

class TestOracle(unittest.TestCase):
	"""What ft_read_<base>_<format> must return, worked out by hand."""

	def test_plain_digits_with_an_optional_minus(self):
		"""101 = 5 in binary; -110 = -6; -2147483647 in base 10."""
		self.assertEqual(output("101", "binary"), "5\n")
		self.assertEqual(output("-110", "binary"), "-6\n")
		self.assertEqual(output("-2147483647", "decimal"), "-2147483647\n")
		self.assertEqual(output("fF", "hex"), "255\n")

	def test_the_prefix_comes_after_the_sign(self):
		"""0o17 = 15; -0o7 = -7; 0x1f = 31."""
		self.assertEqual(output("0o17", "octal", "prefixed"), "15\n")
		self.assertEqual(output("-0o7", "octal", "prefixed"), "-7\n")
		self.assertEqual(output("0x1f", "hex", "prefixed"), "31\n")

	def test_groups_are_cut_by_single_underscores(self):
		"""1_000_000; ff_ff = 65535; 7fff_ffff is the biggest int; -1_0 = -16."""
		self.assertEqual(output("1_000_000", "decimal", "grouped"), "1000000\n")
		self.assertEqual(output("ff_ff", "hex", "grouped"), "65535\n")
		self.assertEqual(output("7fff_ffff", "hex", "grouped"), "2147483647\n")
		self.assertEqual(output("-1_0", "hex", "grouped"), "-16\n")

	def test_anything_but_a_whole_number_gives_0(self):
		"""Spaces, +, a digit out of the base, no digit, a missing prefix, bad underscores."""
		for text in ["", "-", " 1", "1 ", "+1", "102", "12a"]:
			self.assertEqual(output(text, "binary"), "0\n", text)
		for text in ["17", "0o", "0o-7", "0O7"]:
			self.assertEqual(output(text, "octal", "prefixed"), "0\n", text)
		for text in ["a__b", "_a", "a_", "-_1"]:
			self.assertEqual(output(text, "hex", "grouped"), "0\n", text)

class TestVariants(unittest.TestCase):
	"""The variants of number_read."""

	def test_eleven_variants_with_examples_written_for_each_within_80_columns(self):
		"""4 bases x 3 formats, without a prefix in base 10; examples in the variant's form."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 11)
		self.assertNotIn({"base": "decimal", "format": "prefixed"}, combinations)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
		subject = render(Variant(EXERCISE, 0, {"base": "hex", "format": "prefixed"}))
		self.assertIn('ft_read_hex_prefixed("0x2a")\n42$', subject)
		subject = render(Variant(EXERCISE, 0, {"base": "decimal", "format": "grouped"}))
		self.assertIn('ft_read_decimal_grouped("-1_000_000")\n-1000000$', subject)

	def test_generated_tests_are_reproducible_and_read_back(self):
		"""Same seed, same tests; the biggest int and the broken forms are in."""
		params = {"base": "binary", "format": "grouped"}
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		texts = [test.args[0] for test in tests]
		self.assertIn("111_1111_1111_1111_1111_1111_1111_1111", texts)
		for broken in ["", "+100_1101_0010", "_100_1101_0010", "100__1101_0010"]:
			self.assertIn(broken, texts)
