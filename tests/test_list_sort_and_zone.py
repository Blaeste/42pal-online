"""Tests of the list_sort_by and zone_fill exercises (functions).

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
SORT = run_path(str(FOLDER / "list_sort_by/exercise.py"))["EXERCISE"]
ZONE = run_path(str(FOLDER / "zone_fill/exercise.py"))["EXERCISE"]

def sort(numbers, key, order="up"):
	return SORT.oracle({"key": key, "order": order}, TestCase(tuple(map(str, numbers))))

def zone(x, y, rows, connect, measure):
	return ZONE.oracle({"connect": connect, "measure": measure}, TestCase((str(x), str(y), *rows)))

class TestListSort(unittest.TestCase):
	def test_each_key(self):
		self.assertEqual(sort([3, -1, 4, -3, 0, -5], "absolute"), "0 -> -1 -> -3 -> 3 -> 4 -> -5\n")
		self.assertEqual(sort([5, 2, -3, 8], "parity", "down"), "5 -> -3 -> 8 -> 2\n")
		self.assertEqual(sort([21, 13, 40], "last_digit"), "40 -> 21 -> 13\n")
		self.assertEqual(sort([100, -7, 42], "digit_count", "down"), "100 -> 42 -> -7\n")

	def test_empty_and_one_item(self):
		self.assertEqual(sort([], "parity"), "(empty)\n")
		self.assertEqual(sort([7], "absolute", "down"), "7\n")

class TestZone(unittest.TestCase):
	"""1001 / 0110 / 1001: from (0, 0), one cell with four neighbours, six with eight."""

	GRID = ("1001", "0110", "1001")

	def test_size_and_edge(self):
		self.assertEqual(zone(0, 0, self.GRID, "four", "size"), "1001\n0110\n1001\n1\n")
		self.assertEqual(zone(0, 0, self.GRID, "eight", "size"), "1001\n0110\n1001\n6\n")
		self.assertEqual(zone(0, 0, self.GRID, "eight", "edge"), "1001\n0110\n1001\n4\n")
		self.assertEqual(zone(1, 0, self.GRID, "four", "size"), "1001\n0110\n1001\n2\n")

	def test_fill_with_eight_neighbours(self):
		self.assertEqual(zone(0, 0, self.GRID, "eight", "fill"), "F00F\n0FF0\nF00F\n6\n")
		self.assertEqual(zone(0, 0, ("11100", "10100", "11001"), "eight", "fill"),
			"FFF00\nF0F00\nFF001\n7\n")

class TestVariants(unittest.TestCase):
	def test_counts_and_80_columns(self):
		self.assertNotIn({"connect": "four", "measure": "fill"}, ZONE.combinations())
		for exercise, count in [(SORT, 8), (ZONE, 5)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_the_generators_are_reproducible(self):
		for exercise in (SORT, ZONE):
			params = exercise.combinations()[0]
			self.assertEqual(exercise.generate_tests(params, Random(7)),
				exercise.generate_tests(params, Random(7)))
