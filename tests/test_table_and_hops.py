"""Tests of the op_table (a program) and hop_range (a function) exercises.

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

FOLDER = Path(__file__).resolve().parent.parent / "exercises/c"
TABLE = run_path(str(FOLDER / "op_table/exercise.py"))["EXERCISE"]
HOPS = run_path(str(FOLDER / "hop_range/exercise.py"))["EXERCISE"]

def table(args, operation, rows="5"):
	return TABLE.oracle({"operation": operation, "rows": rows}, TestCase(args))

def hops(start, end, step, direction):
	return HOPS.oracle({"step": step, "direction": direction}, TestCase((str(start), str(end))))

class TestTable(unittest.TestCase):
	def test_each_operation(self):
		self.assertEqual(table(("3",), "plus"),
			"1 + 3 = 4\n2 + 3 = 5\n3 + 3 = 6\n4 + 3 = 7\n5 + 3 = 8\n")
		self.assertTrue(table(("3",), "minus").endswith("3 - 5 = -2\n"))
		self.assertTrue(table(("2",), "power").endswith("2 ^ 5 = 32\n"))
		self.assertTrue(table(("50",), "power", "9").endswith("50 ^ 9 = 1953125000000000\n"))
		self.assertEqual(table(("7",), "modulo", "9").splitlines()[1], "7 % 2 = 1")

	def test_wrong_arguments_give_a_newline(self):
		for args in [(), ("0",), ("51",), ("x",), ("1", "2")]:
			self.assertEqual(table(args, "plus"), "\n", args)

class TestHops(unittest.TestCase):
	def test_forward_and_backward(self):
		"""(1, 9) by 3: 1 4 7 from the start, but 9 6 3 from the end."""
		self.assertEqual(hops(1, 10, "3", "forward"), "1 4 7 10\n")
		self.assertEqual(hops(1, 10, "3", "backward"), "10 7 4 1\n")
		self.assertEqual(hops(1, 9, "3", "forward"), "1 4 7\n")
		self.assertEqual(hops(1, 9, "3", "backward"), "9 6 3\n")

	def test_going_down_and_a_single_number(self):
		self.assertEqual(hops(5, -3, "2", "forward"), "5 3 1 -1 -3\n")
		self.assertEqual(hops(5, -3, "5", "backward"), "-3 2\n")
		self.assertEqual(hops(4, 4, "5", "forward"), "4\n")

	def test_the_first_tests_hold_a_single_number_and_both_directions(self):
		tests = HOPS.generate_tests(HOPS.combinations()[0], Random(7))
		self.assertIn(TestCase(("0", "0")), tests[:6])
		self.assertIn(TestCase(("10", "1")), tests[:6])

class TestVariants(unittest.TestCase):
	def test_counts_and_80_columns(self):
		for exercise, count in [(TABLE, 8), (HOPS, 6)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
