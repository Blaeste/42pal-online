"""Tests of the base_string exercise (a function returning a malloc'd string).

The test main prints the string the function returns, then a newline. The
expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/base_string/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(number, base, format="plain"):
	"""What the test main prints for ft_<base>_string_<format>(number)."""
	return EXERCISE.oracle({"base": base, "format": format}, TestCase((str(number),)))

class TestOracle(unittest.TestCase):
	"""What ft_<base>_string_<format> must return, worked out by hand."""

	def test_each_base_plain(self):
		"""255 = ff in hexadecimal; 8 = 10 in octal; 0 is 0 in every base."""
		self.assertEqual(output(255, "hex"), "ff\n")
		self.assertEqual(output(8, "octal"), "10\n")
		self.assertEqual(output(0, "binary"), "0\n")

	def test_prefixed_and_negative(self):
		"""The prefix comes after the sign: -0b10, 0o100, -0xff."""
		self.assertEqual(output(5, "binary", "prefixed"), "0b101\n")
		self.assertEqual(output(-2, "binary", "prefixed"), "-0b10\n")
		self.assertEqual(output(64, "octal", "prefixed"), "0o100\n")
		self.assertEqual(output(-255, "hex", "prefixed"), "-0xff\n")

	def test_the_ends_of_int(self):
		"""-2147483648 = -0x80000000; 2147483647 = 31 ones in binary."""
		self.assertEqual(output(-2147483648, "hex"), "-80000000\n")
		self.assertEqual(output(2147483647, "binary"), "1" * 31 + "\n")

class TestVariants(unittest.TestCase):
	"""The variants of base_string."""

	def test_six_variants_with_examples_within_80_columns(self):
		"""3 bases x 2 formats; each subject shows its calls."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 6)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"{variant.name}(-255)", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_the_ends_of_int_come_first(self):
		"""The first tests (checked by valgrind) hold 0, -1 and both ends of int."""
		tests = EXERCISE.generate_tests(EXERCISE.combinations()[0], Random(7))
		first = [test.args[0] for test in tests[:6]]
		for number in ["0", "-1", "2147483647", "-2147483648"]:
			self.assertIn(number, first)
