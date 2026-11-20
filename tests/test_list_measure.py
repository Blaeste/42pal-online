"""Tests of the list_measure exercise (a function on a linked list, header given).

The test main builds the list from its arguments, calls the function, then
prints the int it returns. The expected outputs below are worked out by
hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/list_measure/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(numbers, measure, cells="all"):
	"""What the test main prints for ft_list_<measure>_<cells> on `numbers`."""
	params = {"measure": measure, "cells": cells}
	return EXERCISE.oracle(params, TestCase(tuple(map(str, numbers))))

class TestOracle(unittest.TestCase):
	"""What ft_list_<measure>_<cells> must return, worked out by hand."""

	def test_each_measure_of_all_the_cells(self):
		"""3 -1 4 -1 5: sum 10, max 5, min -1, one even, two negative."""
		numbers = [3, -1, 4, -1, 5]
		self.assertEqual(output(numbers, "sum"), "10\n")
		self.assertEqual(output(numbers, "max"), "5\n")
		self.assertEqual(output(numbers, "min"), "-1\n")
		self.assertEqual(output(numbers, "count_even"), "1\n")
		self.assertEqual(output(numbers, "count_negative"), "2\n")

	def test_every_other_cell_from_the_first(self):
		"""3 -1 4 -1 5: the cells 3, 4 and 5; -8 2 -6: the cells -8 and -6."""
		self.assertEqual(output([3, -1, 4, -1, 5], "sum", "every_other"), "12\n")
		self.assertEqual(output([3, -1, 4, -1, 5], "count_negative", "every_other"), "0\n")
		self.assertEqual(output([-8, 2, -6], "max", "every_other"), "-6\n")
		self.assertEqual(output([7], "min", "every_other"), "7\n")

	def test_zero_is_even_and_an_empty_list_gives_0(self):
		"""-8 2 -6 0: four even numbers; no cell: 0 for every measure."""
		self.assertEqual(output([-8, 2, -6, 0], "count_even"), "4\n")
		for measure in ["sum", "max", "min", "count_even", "count_negative"]:
			self.assertEqual(output([], measure), "0\n", measure)

class TestVariants(unittest.TestCase):
	"""The variants of list_measure."""

	def test_ten_variants_with_the_header_given_within_80_columns(self):
		"""5 measures x 2; cell.h is given, not expected from the student."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 10)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			self.assertEqual(variant.expected_files, (f"{variant.name}.c",))
			self.assertIn("cell.h", variant.provided_files)
			subject = render(variant)
			self.assertIn("Given files      : cell.h", subject)
			self.assertIn(f"{variant.name}(list) /* 3 -> -1 -> 4 -> -1 -> 5 */", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_tests_are_reproducible_with_an_empty_list(self):
		"""Same seed, same tests; the empty list and a single cell are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(()), tests)
		self.assertIn(TestCase(("7",)), tests)
