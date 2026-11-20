"""Tests of rev_inplace, bit_flip and match_trace: oracles and variants.

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
REV = run_path(str(FOLDER / "rev_inplace/exercise.py"))["EXERCISE"]
FLIP = run_path(str(FOLDER / "bit_flip/exercise.py"))["EXERCISE"]
MATCH = run_path(str(FOLDER / "match_trace/exercise.py"))["EXERCISE"]

def run(exercise, params, *args):
	return exercise.oracle(params, TestCase(args))

class TestOracles(unittest.TestCase):
	def test_rev_inplace(self):
		self.assertEqual(run(REV, {"part": "each_word"}, "hello big world"), "olleh gib dlrow\n")
		self.assertEqual(run(REV, {"part": "letters_only"}, "a-bc!d"), "d-cb!a\n")
		self.assertEqual(run(REV, {"part": "halves"}, "abcdefg"), "defgabc\n")
		self.assertEqual(run(REV, {"part": "inner"}, "abcdefg"), "afedcbg\n")
		self.assertEqual(run(REV, {"part": "inner"}, "ab"), "ab\n")

	def test_bit_flip(self):
		"""38 = 0010 0110."""
		self.assertEqual(run(FLIP, {"part": "each_half"}, "38"), "01000110\n")
		self.assertEqual(run(FLIP, {"part": "pairs"}, "38"), "00011001\n")
		self.assertEqual(run(FLIP, {"part": "middle_six"}, "38"), "01100100\n")

	def test_match_trace(self):
		self.assertEqual(run(MATCH, {"what": "marked", "case": "exact"}, "abc", "xaybzc"), "xAyBzC\n")
		self.assertEqual(run(MATCH, {"what": "skipped", "case": "exact"}, "abc", "xaybzc"), "xyz\n")
		self.assertEqual(run(MATCH, {"what": "prefix", "case": "exact"}, "abc", "acb"), "ab\n")
		self.assertEqual(run(MATCH, {"what": "marked", "case": "exact"}, "abc", "acb"), "\n")
		self.assertEqual(run(MATCH, {"what": "skipped", "case": "any_case"}, "ABC", "xaybzc"), "xyz\n")

class TestVariants(unittest.TestCase):
	def test_counts_and_80_columns(self):
		for exercise, count in [(REV, 4), (FLIP, 3), (MATCH, 6)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
