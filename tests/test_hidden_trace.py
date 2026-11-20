"""Tests of the hidden_trace exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/hidden_trace/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, what, case="exact"):
	return EXERCISE.oracle({"what": what, "case": case}, TestCase(args))

class TestOracle(unittest.TestCase):
	def test_abc_in_xaxbxc(self):
		"""a b c are at 1 3 5; the shortest part holding them is axbxc; read backwards, no."""
		self.assertEqual(output(("abc", "xaxbxc"), "positions"), "1 3 5\n")
		self.assertEqual(output(("abc", "xaxbxc"), "window"), "5\n")
		self.assertEqual(output(("abc", "xaxbxc"), "backwards"), "0\n")
		self.assertEqual(output(("cba", "xaxbxc"), "backwards"), "1\n")

	def test_the_first_letters_found_and_the_shortest_part(self):
		"""In aXXabYb: a at 0 and b at 4 first; but ab at 3 is the shortest part."""
		self.assertEqual(output(("ab", "aXXabYb"), "positions"), "0 4\n")
		self.assertEqual(output(("ab", "aXXabYb"), "window"), "2\n")

	def test_any_case_and_not_hidden(self):
		self.assertEqual(output(("AB", "xaxB"), "positions", "any_case"), "1 3\n")
		self.assertEqual(output(("AB", "xaxB"), "positions"), "\n")
		self.assertEqual(output(("abc", "acb"), "window"), "0\n")

	def test_an_empty_first_string_and_wrong_arguments(self):
		self.assertEqual(output(("", "abc"), "window"), "0\n")
		self.assertEqual(output(("", "abc"), "backwards"), "1\n")
		for args in [(), ("a",), ("a", "b", "c")]:
			self.assertEqual(output(args, "window"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_six_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 6)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
