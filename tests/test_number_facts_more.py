"""Tests of the prime_facts and divisor_facts exercises (programs).

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

FOLDER = Path(__file__).resolve().parent.parent / "exercises/c"
PRIMES = run_path(str(FOLDER / "prime_facts/exercise.py"))["EXERCISE"]
DIVISORS = run_path(str(FOLDER / "divisor_facts/exercise.py"))["EXERCISE"]

def primes(args, measure, range_="up_to"):
	return PRIMES.oracle({"measure": measure, "range": range_}, TestCase(args))

def divisors(args, what):
	return DIVISORS.oracle({"what": what}, TestCase(args))

class TestPrimes(unittest.TestCase):
	def test_up_to_ten_and_between_ten_and_twenty(self):
		"""2 3 5 7; 11 13 17 19."""
		self.assertEqual(primes(("10",), "count"), "4\n")
		self.assertEqual(primes(("10",), "largest"), "7\n")
		self.assertEqual(primes(("10",), "digit_sum"), "17\n")
		self.assertEqual(primes(("10",), "largest", "between"), "19\n")
		self.assertEqual(primes(("10",), "digit_sum", "between"), "24\n")

	def test_one_and_wrong_arguments(self):
		self.assertEqual(primes(("1",), "largest"), "0\n")
		self.assertEqual(primes(("1",), "count", "between"), "1\n")
		for args in [(), ("0",), ("-5",), ("12a",), ("1", "2")]:
			self.assertEqual(primes(args, "count"), "0\n", args)

class TestDivisors(unittest.TestCase):
	def test_twelve_and_eighteen(self):
		self.assertEqual(divisors(("12", "18"), "common_count"), "4\n")
		self.assertEqual(divisors(("12", "18"), "common_list"), "1 2 3 6\n")
		self.assertEqual(divisors(("12", "18"), "coprime"), "no\n")
		self.assertEqual(divisors(("12", "18"), "euclid_steps"), "12 18 12 6\n")

	def test_coprime_numbers_and_wrong_arguments(self):
		self.assertEqual(divisors(("7", "9"), "coprime"), "yes\n")
		self.assertEqual(divisors(("48", "18"), "euclid_steps"), "48 18 12 6\n")
		for args in [(), ("4",), ("4", "0"), ("4", "x"), ("1", "2", "3")]:
			self.assertEqual(divisors(args, "coprime"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_counts_and_80_columns(self):
		for exercise, count in [(PRIMES, 6), (DIVISORS, 4)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
