"""Tests of the first piscine models: letter_find, set_first, char_only, char_line.

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
FIND = run_path(str(FOLDER / "letter_find/exercise.py"))["EXERCISE"]
FIRST = run_path(str(FOLDER / "set_first/exercise.py"))["EXERCISE"]
ONLY = run_path(str(FOLDER / "char_only/exercise.py"))["EXERCISE"]
LINE = run_path(str(FOLDER / "char_line/exercise.py"))["EXERCISE"]

def run(exercise, params, *args):
	return exercise.oracle(params, TestCase(args))

class TestOracles(unittest.TestCase):
	def test_letter_find(self):
		self.assertEqual(run(FIND, {"letter": "e", "case": "exact"}, "Hello"), "e\n")
		self.assertEqual(run(FIND, {"letter": "e", "case": "exact"}, "HELLO"), "\n")
		self.assertEqual(run(FIND, {"letter": "e", "case": "any_case"}, "HELLO"), "E\n")
		self.assertEqual(run(FIND, {"letter": "s", "case": "exact"}), "s\n")

	def test_set_first(self):
		self.assertEqual(run(FIRST, {"set": "digit", "fallback": "dash"}, "ab3c4"), "3\n")
		self.assertEqual(run(FIRST, {"set": "digit", "fallback": "dash"}, "abc"), "-\n")
		self.assertEqual(run(FIRST, {"set": "upper", "fallback": "question"}, "hello World"), "W\n")
		self.assertEqual(run(FIRST, {"set": "punct", "fallback": "dash"}, "Hi, you!"), ",\n")
		self.assertEqual(run(FIRST, {"set": "vowel", "fallback": "question"}), "?\n")

	def test_char_only_and_char_line(self):
		self.assertEqual(run(ONLY, {"char": "k", "end": "bare"}, "x"), "k")
		self.assertEqual(run(ONLY, {"char": "7", "end": "newline"}), "7\n")
		self.assertEqual(run(LINE, {"char": "hash", "count": "5"}), "#####\n")
		self.assertEqual(run(LINE, {"char": "equal", "count": "10"}, "a"), "==========\n")

class TestVariants(unittest.TestCase):
	def test_counts_and_80_columns(self):
		for exercise, count in [(FIND, 6), (FIRST, 8), (ONLY, 8), (LINE, 6)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")

SAY = run_path(str(FOLDER / "say_message/exercise.py"))["EXERCISE"]
COUNT = run_path(str(FOLDER / "count_down/exercise.py"))["EXERCISE"]
PARAM = run_path(str(FOLDER / "param_from_end/exercise.py"))["EXERCISE"]

class TestMoreOracles(unittest.TestCase):
	def test_say_message_and_count_down(self):
		self.assertEqual(run(SAY, {"message": "good_morning", "case": "upper"}), "GOOD MORNING!\n")
		self.assertEqual(run(SAY, {"message": "forty_two", "case": "as_is"}, "x"), "42 is the answer.\n")
		self.assertEqual(run(COUNT, {"start": "5", "separator": "space"}), "5 4 3 2 1 0\n")
		self.assertEqual(run(COUNT, {"start": "12", "separator": "comma"}),
			"12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0\n")

	def test_param_from_end(self):
		self.assertEqual(run(PARAM, {"which": "second_last", "how": "plain"}, "a", "Bc", "dEf"), "Bc\n")
		self.assertEqual(run(PARAM, {"which": "last_two", "how": "upper"}, "a", "Bc", "dEf"), "BC DEF\n")
		self.assertEqual(run(PARAM, {"which": "last_two", "how": "reversed"}, "a", "Bc", "dEf"), "cB fEd\n")
		self.assertEqual(run(PARAM, {"which": "second_last", "how": "plain"}, "alone"), "\n")

	def test_more_counts_and_80_columns(self):
		for exercise, count in [(SAY, 6), (COUNT, 6), (PARAM, 6)]:
			self.assertEqual(len(exercise.combinations()), count)
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
