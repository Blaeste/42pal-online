"""Tests of the number_facts exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/number_facts/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, what, separator="space"):
	"""What the program prints for these arguments and params."""
	return EXERCISE.oracle({"what": what, "separator": separator}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What <what>_<separator> must print, worked out by hand."""

	def test_divisors_prime_divisors_and_primes(self):
		"""12: 1 2 3 4 6 12; 360 = 2^3 x 3^2 x 5; primes up to 10: 2 3 5 7."""
		self.assertEqual(output(("12",), "divisors"), "1 2 3 4 6 12\n")
		self.assertEqual(output(("360",), "prime_divisors", "comma"), "2, 3, 5\n")
		self.assertEqual(output(("10",), "primes_up_to", "newline"), "2\n3\n5\n7\n")
		self.assertEqual(output(("13",), "divisors"), "1 13\n")
		self.assertEqual(output(("007",), "divisors"), "1 7\n")

	def test_one_has_no_prime(self):
		"""1 divides 1, but no prime number divides it or is below it."""
		self.assertEqual(output(("1",), "divisors"), "1\n")
		self.assertEqual(output(("1",), "prime_divisors"), "\n")
		self.assertEqual(output(("1",), "primes_up_to"), "\n")

	def test_anything_but_one_positive_number_prints_a_newline(self):
		"""Not 1 argument, 0, a sign, a letter, empty, or more than 6 digits."""
		for args in [(), ("1", "2"), ("0",), ("-4",), ("12a",), ("",), ("1234567",)]:
			self.assertEqual(output(args, "divisors"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants of number_facts."""

	def test_nine_variants_within_80_columns(self):
		"""3 lists x 3 separators: no combination gives back a real subject."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 9)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_the_bad_arguments(self):
		"""Same seed, same tests; 0, a sign and a letter are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		for bad in ["0", "-4", "12a"]:
			self.assertIn(TestCase((bad,)), tests)
