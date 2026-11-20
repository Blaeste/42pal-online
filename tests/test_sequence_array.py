"""Tests of the sequence_array exercise (a function returning a malloc'd array).

The test main prints the n ints of the array the function returns, separated
by spaces, then a newline. The expected outputs below are worked out by hand,
never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/sequence_array/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(n, sequence, order="up"):
	"""What the test main prints for ft_<sequence>_<order>(n)."""
	return EXERCISE.oracle({"sequence": sequence, "order": order}, TestCase((str(n),)))

class TestOracle(unittest.TestCase):
	"""What ft_<sequence>_<order> must return, worked out by hand."""

	def test_each_sequence_up(self):
		"""The first terms, in the order of the sequence."""
		self.assertEqual(output(5, "squares"), "0 1 4 9 16\n")
		self.assertEqual(output(5, "triangles"), "0 1 3 6 10\n")
		self.assertEqual(output(8, "fibonacci"), "0 1 1 2 3 5 8 13\n")
		self.assertEqual(output(4, "odds"), "1 3 5 7\n")
		self.assertEqual(output(6, "powers_of_two"), "1 2 4 8 16 32\n")

	def test_down_starts_with_the_last_term(self):
		"""The same terms, the n-th one first."""
		self.assertEqual(output(5, "triangles", "down"), "10 6 3 1 0\n")
		self.assertEqual(output(4, "odds", "down"), "7 5 3 1\n")
		self.assertEqual(output(1, "fibonacci", "down"), "0\n")

	def test_thirty_one_terms_still_fit_in_an_int(self):
		"""2 to the power 30 = 1073741824; the 31st Fibonacci number is 832040."""
		self.assertTrue(output(31, "powers_of_two").endswith(" 1073741824\n"))
		self.assertTrue(output(31, "fibonacci", "down").startswith("832040 514229 "))

	def test_zero_or_less_gives_null(self):
		"""No array for n <= 0: the test main prints (null)."""
		for n in [0, -5, -2147483648]:
			self.assertEqual(output(n, "squares"), "(null)\n", n)

class TestVariants(unittest.TestCase):
	"""The variants of sequence_array."""

	def test_ten_variants_with_examples_within_80_columns(self):
		"""5 sequences x 2 orders; each subject shows its calls."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 10)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"{variant.name}(6)", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_the_edge_cases_come_first(self):
		"""Same seed, same tests; the first 6 (checked by valgrind) hold 0, -5, 1 and 31."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		first = [test.args[0] for test in tests[:6]]
		for n in ["0", "-5", "1", "31"]:
			self.assertIn(n, first)
