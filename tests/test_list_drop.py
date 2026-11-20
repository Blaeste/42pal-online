"""Tests of the list_drop exercise (a function on a linked list, with a header).

The test main builds the list from its arguments, calls the function, then
prints the values left, from the first node: "2 -> 3", or "(empty)". The
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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/list_drop/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(values, which, condition):
	"""What the test main prints after ft_drop_<which>_<condition> on `values`."""
	params = {"which": which, "condition": condition}
	return EXERCISE.oracle(params, TestCase(tuple(map(str, values))))

class TestOracle(unittest.TestCase):
	"""What is left after ft_drop_<which>_<condition>, worked out by hand."""

	def test_all_first_or_last_of_the_matching_nodes(self):
		"""In 2 2 3 -4 -4 5 2, the even values are at the start, in the middle, at the end."""
		values = [2, 2, 3, -4, -4, 5, 2]
		self.assertEqual(output(values, "all", "even"), "3 -> 5\n")
		self.assertEqual(output(values, "first", "even"), "2 -> 3 -> -4 -> -4 -> 5 -> 2\n")
		self.assertEqual(output(values, "last", "even"), "2 -> 2 -> 3 -> -4 -> -4 -> 5\n")
		self.assertEqual(output(values, "all", "negative"), "2 -> 2 -> 3 -> 5 -> 2\n")

	def test_repeated_values_are_the_ones_seen_before(self):
		"""In 7 8 7 -6 8 9, the second 7 and the second 8 are repeated."""
		values = [7, 8, 7, -6, 8, 9]
		self.assertEqual(output(values, "all", "repeated"), "7 -> 8 -> -6 -> 9\n")
		self.assertEqual(output(values, "first", "repeated"), "7 -> 8 -> -6 -> 8 -> 9\n")
		self.assertEqual(output(values, "last", "repeated"), "7 -> 8 -> 7 -> -6 -> 9\n")

	def test_negative_odd_values_are_odd_and_zero_is_even(self):
		"""-1 is odd; 0 is even."""
		self.assertEqual(output([-1, -1, -1], "all", "odd"), "(empty)\n")
		self.assertEqual(output([0, 1], "first", "even"), "1\n")

	def test_nothing_to_drop_or_an_empty_list(self):
		"""No matching node leaves the list as it was; no node at all gives (empty)."""
		self.assertEqual(output([1, 2], "all", "negative"), "1 -> 2\n")
		self.assertEqual(output([], "last", "odd"), "(empty)\n")

class TestVariants(unittest.TestCase):
	"""The variants of list_drop."""

	def test_twelve_variants_with_examples_within_80_columns(self):
		"""3 x 4; each subject asks for node.h and shows the list before each call."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 12)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			self.assertEqual(variant.expected_files[1], "node.h")
			subject = render(variant)
			self.assertIn(f"{variant.name}(&list) /* 7 -> 8 -> 7 -> -6 -> 8 -> 9 */", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_the_subject_shows_the_header_next_to_ref_c(self):
		"""The node.h the student must write is the one check-catalog hands in."""
		header = (EXERCISE_FILE.parent / "node.h").read_text(encoding="utf-8")
		subject = render(Variant(EXERCISE, 0, EXERCISE.combinations()[0]))
		self.assertIn(header, subject)
		self.assertIn("int\t\t\t\tvalue;", header)

	def test_the_first_tests_drop_the_first_nodes(self):
		"""Same seed, same tests; the first 6 (checked by valgrind) drop at the start."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(()), tests[:6])
		self.assertIn(TestCase(("2", "2", "3", "-4", "-4", "5", "2")), tests[:6])
		self.assertIn(TestCase(("-1", "-1", "-1")), tests[:6])
