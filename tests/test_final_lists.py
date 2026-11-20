"""Tests of list_loop and list_each (functions on linked lists, header given).

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
LOOP = run_path(str(FOLDER / "list_loop/exercise.py"))["EXERCISE"]
EACH = run_path(str(FOLDER / "list_each/exercise.py"))["EXERCISE"]

def loop(what, *args):
	return LOOP.oracle({"what": what}, TestCase(args))

def each(which, *values):
	return EACH.oracle({"which": which}, TestCase(values))

class TestLoop(unittest.TestCase):
	def test_a_loop_back_to_node_1(self):
		"""1 -> 2 -> 3 -> back to node 1: the loop is 2 3, after one node."""
		self.assertEqual(loop("length", "1", "1", "2", "3"), "2\n")
		self.assertEqual(loop("start", "1", "1", "2", "3"), "1\n")
		self.assertEqual(loop("before", "1", "1", "2", "3"), "1\n")

	def test_no_loop_a_node_on_itself_and_an_empty_list(self):
		self.assertEqual(loop("before", "-1", "1", "2", "3"), "3\n")
		self.assertEqual(loop("length", "0", "5"), "1\n")
		self.assertEqual(loop("start", "-1"), "-1\n")

class TestEach(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(each("every_other", "3", "-1", "4", "-1", "5"), "f got: 3 4 5\nlist: 6 -1 8 -1 10\n")
		self.assertEqual(each("backwards", "1", "2", "3"), "f got: 3 2 1\nlist: 2 4 6\n")
		self.assertEqual(each("while_positive", "1", "2", "0", "4"), "f got: 1 2\nlist: 2 4 0 4\n")
		self.assertEqual(each("from_second", "1", "2", "3"), "f got: 2 3\nlist: 1 4 6\n")
		self.assertEqual(each("backwards"), "f got:\nlist:\n")

class TestVariants(unittest.TestCase):
	def test_counts_and_80_columns(self):
		for exercise, count in [(LOOP, 3), (EACH, 4)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
