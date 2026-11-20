"""Tests of set_run and set_find: functions that test the characters of a
string against a set given as a second string.

set_run measures a run of characters of the set; set_find returns a pointer
to a character in, or out of, the set. The test main prints the size, or
the index and the rest of the string. The expected outputs below are worked
out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISES = Path(__file__).resolve().parent.parent / "exercises/c"
SET_RUN = run_path(str(EXERCISES / "set_run/exercise.py"))["EXERCISE"]
SET_FIND = run_path(str(EXERCISES / "set_find/exercise.py"))["EXERCISE"]

def run(text, chars, kind):
	return SET_RUN.oracle({"kind": kind}, TestCase((text, chars)))

def find(text, chars, kind):
	return SET_FIND.oracle({"kind": kind}, TestCase((text, chars)))

class TestSetRun(unittest.TestCase):
	def test_each_kind_of_run(self):
		"""aabxbba with the set ab: 3 at the end, 3 the longest, 3 first, 6 in all."""
		self.assertEqual(run("aabxbba", "ab", "end"), "3\n")
		self.assertEqual(run("aabxbba", "ab", "longest"), "3\n")
		self.assertEqual(run("aabxbba", "ab", "first"), "3\n")
		self.assertEqual(run("aabxbba", "ab", "count"), "6\n")

	def test_the_first_run_skips_what_is_not_in_the_set(self):
		"""--12-345 with the digits: the first run is 12, the longest 345."""
		digits = "0123456789"
		self.assertEqual(run("--12-345", digits, "first"), "2\n")
		self.assertEqual(run("--12-345", digits, "longest"), "3\n")
		self.assertEqual(run("--12-345", digits, "end"), "3\n")
		self.assertEqual(run("--12-345", digits, "count"), "5\n")

	def test_empty_string_empty_set_or_no_match(self):
		for kind in ("end", "longest", "first", "count"):
			self.assertEqual(run("", "ab", kind), "0\n")
			self.assertEqual(run("hello", "", kind), "0\n")
			self.assertEqual(run("xyz", "abc", kind), "0\n")

	def test_no_variant_is_the_real_subject(self):
		"""The run at the start of s, the real subject, is not one of the kinds."""
		self.assertNotIn("start", SET_RUN.params[0].values)

class TestSetFind(unittest.TestCase):
	def test_each_kind_of_search(self):
		"""hello world with the set ow."""
		self.assertEqual(find("hello world", "ow", "last"), "7: orld\n")
		self.assertEqual(find("hello world", "ow", "first_out"), "0: hello world\n")
		self.assertEqual(find("hello world", "ow", "last_out"), "10: d\n")
		self.assertEqual(find("hello world", "ow", "pair"), "6: world\n")

	def test_repeated_characters(self):
		self.assertEqual(find("aaab", "a", "last"), "2: ab\n")
		self.assertEqual(find("aaab", "a", "first_out"), "3: b\n")
		self.assertEqual(find("aaab", "a", "last_out"), "3: b\n")
		self.assertEqual(find("aaab", "a", "pair"), "0: aaab\n")

	def test_null_when_there_is_no_such_character(self):
		self.assertEqual(find("abc", "xyz", "last"), "NULL\n")
		self.assertEqual(find("abc", "xyz", "pair"), "NULL\n")
		self.assertEqual(find("aaa", "a", "first_out"), "NULL\n")
		self.assertEqual(find("aaa", "a", "last_out"), "NULL\n")
		for kind in ("last", "first_out", "last_out", "pair"):
			self.assertEqual(find("", "a", kind), "NULL\n")

	def test_no_variant_is_the_real_subject(self):
		"""The first character in the set, the real subject, is not one of the kinds."""
		self.assertNotIn("first", SET_FIND.params[0].values)

class TestSubjects(unittest.TestCase):
	def test_four_variants_each_within_80_columns(self):
		for exercise in (SET_RUN, SET_FIND):
			combinations = exercise.combinations()
			self.assertEqual(len(combinations), 4)
			for params in combinations:
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{params} : {line}")
