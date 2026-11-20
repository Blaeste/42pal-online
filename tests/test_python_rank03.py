"""Tests of the Python models of the rank 03: one per style of the real exam.

Each test calls the oracle of a variant on values chosen by hand; the
expected results are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.python_exercise import case
from pal42.subject import render
from pal42.variant import Variant

EXERCISES = Path(__file__).resolve().parent.parent / "exercises/python"
NAMES = ("nest_check", "key_sort", "mirror_word", "grid_turn", "trace_letters", "char_mix",
	"base_shift", "digit_steps", "letter_bag", "merge_twist", "char_balance", "case_wave",
	"shift_list", "key_shift")
LOADED = {name: run_path(str(EXERCISES / name / "exercise.py"))["EXERCISE"] for name in NAMES}

def result(name, params, *values):
	"""What the test main prints for the call, without its newline."""
	return LOADED[name].oracle(params, case(*values)).removesuffix("\n")

class TestNestCheck(unittest.TestCase):
	def test_pairs(self):
		self.assertEqual(result("nest_check", {"report": "pairs", "kinds": "two"}, "a(b[c])()"), "3")
		self.assertEqual(result("nest_check", {"report": "pairs", "kinds": "two"}, "([)]"), "-1")
		self.assertEqual(result("nest_check", {"report": "pairs", "kinds": "two"}, "{<"), "0")
		self.assertEqual(result("nest_check", {"report": "pairs", "kinds": "four"}, "{<"), "-1")

	def test_deepest(self):
		self.assertEqual(result("nest_check", {"report": "deepest", "kinds": "two"}, "a(b[c])(d)"), "3")
		self.assertEqual(result("nest_check", {"report": "deepest", "kinds": "four"}, "<>{[()]}"), "4")
		self.assertEqual(result("nest_check", {"report": "deepest", "kinds": "two"}, "abc"), "-1")
		self.assertEqual(result("nest_check", {"report": "deepest", "kinds": "two"}, "(("), "-1")

	def test_repair(self):
		self.assertEqual(result("nest_check", {"report": "repair", "kinds": "four"}, "({<a"), "'({<a>})'")
		self.assertEqual(result("nest_check", {"report": "repair", "kinds": "two"}, "(]"), "None")
		self.assertEqual(result("nest_check", {"report": "repair", "kinds": "two"}, "{x"), "'{x'")

class TestKeySort(unittest.TestCase):
	def test_consonants_then_lower_case(self):
		words = ["street", "Aia", "bob", "eau", "Bob", "tree"]
		self.assertEqual(result("key_sort", {"rule": "consonants"}, words),
			"['Aia', 'eau', 'bob', 'Bob', 'tree', 'street']")

	def test_last_char_then_longest(self):
		self.assertEqual(result("key_sort", {"rule": "last_char"}, ["ab", "", "zzb", "a", "Ba"]),
			"['', 'Ba', 'a', 'zzb', 'ab']")

	def test_most_digits_then_shortest(self):
		self.assertEqual(result("key_sort", {"rule": "digits"}, ["a1", "b22", "c", "1d2", "x"]),
			"['b22', '1d2', 'a1', 'c', 'x']")

class TestMirrorWord(unittest.TestCase):
	def test_digits(self):
		self.assertEqual(result("mirror_word", {"rule": "digits"}, "1a2b-3"), "False")
		self.assertEqual(result("mirror_word", {"rule": "digits"}, "12x21"), "True")
		self.assertEqual(result("mirror_word", {"rule": "digits"}, "no digit"), "True")

	def test_longest_word(self):
		self.assertEqual(result("mirror_word", {"rule": "longest_word"}, "Anna saw a Kayak at noon"),
			"'Kayak'")
		self.assertEqual(result("mirror_word", {"rule": "longest_word"}, "abc de"), "''")

	def test_near(self):
		self.assertEqual(result("mirror_word", {"rule": "near"}, "Ra-ce car"), "True")
		self.assertEqual(result("mirror_word", {"rule": "near"}, "abca"), "True")
		self.assertEqual(result("mirror_word", {"rule": "near"}, "abcda"), "False")

class TestGridTurn(unittest.TestCase):
	GRID = [[1, 2, 3], [4, 5, 6]]

	def test_each_move(self):
		self.assertEqual(result("grid_turn", {"move": "upside_down"}, self.GRID), "[[4, 5, 6], [1, 2, 3]]")
		self.assertEqual(result("grid_turn", {"move": "transpose"}, self.GRID), "[[1, 4], [2, 5], [3, 6]]")
		self.assertEqual(result("grid_turn", {"move": "rotate_right"}, self.GRID), "[[4, 1], [5, 2], [6, 3]]")
		self.assertEqual(result("grid_turn", {"move": "rotate_left"}, self.GRID), "[[3, 6], [2, 5], [1, 4]]")
		self.assertEqual(result("grid_turn", {"move": "transpose"}, []), "[]")

class TestTraceLetters(unittest.TestCase):
	def test_positions(self):
		self.assertEqual(result("trace_letters", {"rule": "positions"}, "abc", "xaxbxcx"), "[1, 3, 5]")
		self.assertEqual(result("trace_letters", {"rule": "positions"}, "abc", "cba"), "None")
		self.assertEqual(result("trace_letters", {"rule": "positions"}, "", "abc"), "[]")

	def test_count(self):
		self.assertEqual(result("trace_letters", {"rule": "count"}, "ab", "aabb ab"), "2")
		self.assertEqual(result("trace_letters", {"rule": "count"}, "ab", "ba"), "0")
		self.assertEqual(result("trace_letters", {"rule": "count"}, "", "ab"), "0")

	def test_nocase(self):
		self.assertEqual(result("trace_letters", {"rule": "nocase"}, "AbC", "xaYBzc"), "True")
		self.assertEqual(result("trace_letters", {"rule": "nocase"}, "ab", "BA"), "False")

class TestCharMix(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("char_mix", {"rule": "only_first"}, "hello", "world"), "'he'")
		self.assertEqual(result("char_mix", {"rule": "one_side"}, "hello", "world"), "'hewrd'")
		self.assertEqual(result("char_mix", {"rule": "common_count"}, "hello", "world"), "{'l': 1, 'o': 1}")
		self.assertEqual(result("char_mix", {"rule": "common_count"}, "aab", "baaa"), "{'a': 2, 'b': 1}")

class TestBaseShift(unittest.TestCase):
	def test_to_decimal(self):
		self.assertEqual(result("base_shift", {"op": "to_decimal"}, "ff", 16), "'255'")
		self.assertEqual(result("base_shift", {"op": "to_decimal"}, "-101", 2), "'-5'")
		self.assertEqual(result("base_shift", {"op": "to_decimal"}, "12", 2), "None")
		self.assertEqual(result("base_shift", {"op": "to_decimal"}, "1", 37), "None")

	def test_from_decimal(self):
		self.assertEqual(result("base_shift", {"op": "from_decimal"}, "255", 16), "'FF'")
		self.assertEqual(result("base_shift", {"op": "from_decimal"}, "-5", 2), "'-101'")
		self.assertEqual(result("base_shift", {"op": "from_decimal"}, "0", 36), "'0'")
		self.assertEqual(result("base_shift", {"op": "from_decimal"}, "1a", 16), "None")

	def test_next(self):
		self.assertEqual(result("base_shift", {"op": "next"}, "FF", 16), "'100'")
		self.assertEqual(result("base_shift", {"op": "next"}, "-10", 2), "'-1'")
		self.assertEqual(result("base_shift", {"op": "next"}, "-1", 7), "'0'")
		self.assertEqual(result("base_shift", {"op": "next"}, "", 10), "None")

class TestDigitSteps(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("digit_steps", {"rule": "down"}, "3210a98"), "4")
		self.assertEqual(result("digit_steps", {"rule": "equal"}, "111x22"), "3")
		self.assertEqual(result("digit_steps", {"rule": "longest_run"}, "x1234y56"), "4")
		self.assertEqual(result("digit_steps", {"rule": "longest_run"}, "97"), "1")
		self.assertEqual(result("digit_steps", {"rule": "longest_run"}, "none"), "0")
		self.assertEqual(result("digit_steps", {"rule": "wrap_up"}, "8901 23"), "4")

class TestLetterBag(unittest.TestCase):
	def test_missing(self):
		self.assertEqual(result("letter_bag", {"rule": "missing"}, "Hello", "hello world"), "'dlorw'")
		self.assertEqual(result("letter_bag", {"rule": "missing"}, "abc", "CAB!"), "''")

	def test_groups(self):
		self.assertEqual(result("letter_bag", {"rule": "groups"}, ["Listen", "pots", "silent", "stop", "x"]),
			"[['Listen', 'silent'], ['pots', 'stop'], ['x']]")

	def test_can_write(self):
		self.assertEqual(result("letter_bag", {"rule": "can_write"}, "Tea", "a tree"), "True")
		self.assertEqual(result("letter_bag", {"rule": "can_write"}, "teet", "a tree"), "False")

class TestMergeTwist(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("merge_twist", {"rule": "descending"}, [9, 4, 1], [8, 4]), "[9, 8, 4, 4, 1]")
		self.assertEqual(result("merge_twist", {"rule": "unique"}, [1, 1, 3], [1, 2, 3, 3]), "[1, 2, 3]")
		self.assertEqual(result("merge_twist", {"rule": "path"}, [1, 4], [2, 3]), "'abba'")
		self.assertEqual(result("merge_twist", {"rule": "path"}, [2], [1, 2]), "'bab'")

class TestCharBalance(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("char_balance", {"rule": "changes"}, "aabc", "abcd"), "1")
		self.assertEqual(result("char_balance", {"rule": "changes"}, "ab", "abc"), "-1")
		self.assertEqual(result("char_balance", {"rule": "first_extra"}, "banana", "abn"), "'a'")
		self.assertEqual(result("char_balance", {"rule": "first_extra"}, "ab", "ba"), "''")
		self.assertEqual(result("char_balance", {"rule": "window"}, "ab", "xxbay"), "2")
		self.assertEqual(result("char_balance", {"rule": "window"}, "aB", "abba"), "-1")

class TestCaseWave(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("case_wave", {"rule": "words"}, "hello big world"), "'HeLlO BiG WoRlD'")
		self.assertEqual(result("case_wave", {"rule": "pattern"}, "a-bcd e", "uul"), "'A-BcD E'")
		self.assertEqual(result("case_wave", {"rule": "all_chars"}, "abcd ef"), "'AbCd eF'")

class TestShiftList(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("shift_list", {"rule": "left"}, [1, 2, 3, 4], 5), "[2, 3, 4, 1]")
		self.assertEqual(result("shift_list", {"rule": "left"}, [], 3), "[]")
		self.assertEqual(result("shift_list", {"rule": "blocks"}, [1, 2, 3, 4, 5, 6, 7], 3),
			"[3, 2, 1, 6, 5, 4, 7]")
		self.assertEqual(result("shift_list", {"rule": "keep_negatives"}, [1, -1, 2, 3, -5], 1),
			"[3, -1, 1, 2, -5]")

class TestKeyShift(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("key_shift", {"rule": "by_key"}, "Hello, World", "abc"), "'Hfnlp, Yosnd'")
		self.assertEqual(result("key_shift", {"rule": "growing"}, "aaa-a", 2), "'ace-g'")
		self.assertEqual(result("key_shift", {"rule": "growing"}, "Zz", -1), "'Zy'")
		self.assertEqual(result("key_shift", {"rule": "with_digits"}, "Zz 09!", 3), "'Cc 32!'")
		self.assertEqual(result("key_shift", {"rule": "with_digits"}, "a0", -1), "'z9'")

class TestSubjects(unittest.TestCase):
	def test_every_variant_renders_within_80_columns(self):
		for name, exercise in LOADED.items():
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line.expandtabs(4)), 80, f"{name} {params}: {line}")
