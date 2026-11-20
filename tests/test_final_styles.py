"""Tests of the last five styles of the piscine final exam: board_threat,
tape_script, byte_dump, flag_mask and expr_eval.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISES = Path(__file__).resolve().parent.parent / "exercises/c"

def load(name):
	return run_path(str(EXERCISES / name / "exercise.py"))["EXERCISE"]

BOARD_THREAT = load("board_threat")
TAPE_SCRIPT = load("tape_script")
BYTE_DUMP = load("byte_dump")
FLAG_MASK = load("flag_mask")
EXPR_EVAL = load("expr_eval")

def out(exercise, params, *args):
	return exercise.oracle(params, TestCase(tuple(args)))

class TestBoardThreat(unittest.TestCase):
	"""Pieces of our own on a board given row by row: which ones attack T."""

	def threat(self, pieces, answer, *rows):
		return out(BOARD_THREAT, {"pieces": pieces, "answer": answer}, *rows)

	def test_knights_jump_over_everything(self):
		rows = ("N....", "..T..", "....N", ".N...")
		self.assertEqual(self.threat("knights", "count", *rows), "3\n")
		self.assertEqual(self.threat("knights", "where", *rows), "1,1\n3,5\n4,2\n")

	def test_guards_attack_the_eight_squares_around(self):
		rows = ("G..", ".T.", "..G", "G..")
		self.assertEqual(self.threat("guards", "count", *rows), "2\n")
		self.assertEqual(self.threat("guards", "where", *rows), "1,1\n3,3\n")

	def test_lines_stop_at_the_first_square_that_is_not_empty(self):
		rows = ("L.T.L", ".....", "..L..", "..L..")
		self.assertEqual(self.threat("lines", "count", *rows), "3\n")
		self.assertEqual(self.threat("lines", "where", *rows), "1,1\n1,5\n3,3\n")

	def test_mixed_and_the_other_letters_are_empty_squares(self):
		rows = ("N.L..", "..T.G", "G...L", "..L.N")
		self.assertEqual(self.threat("mixed", "where", *rows), "1,1\n1,3\n4,3\n")
		self.assertEqual(self.threat("knights", "count", *rows), "1\n")
		self.assertEqual(self.threat("lines", "count", *rows), "2\n")
		self.assertEqual(self.threat("guards", "count", *rows), "0\n")
		self.assertEqual(self.threat("guards", "where", *rows), "safe\n")

	def test_no_argument_gives_a_newline(self):
		self.assertEqual(self.threat("mixed", "count"), "\n")

class TestTapeScript(unittest.TestCase):
	"""A tape of bytes, with loops of our own: times, countdown and if."""

	def run_script(self, loop, show, script):
		return out(TAPE_SCRIPT, {"loop": loop, "print": show}, script)

	def test_times_repeats_the_body_the_number_of_times_after_it(self):
		self.assertEqual(self.run_script("times", "char", "(+++++++++)8.>((+++++)3)7."), "Hi")
		self.assertEqual(self.run_script("times", "number", "(+)3.>((++)2)3."), "3\n12\n")
		self.assertEqual(self.run_script("times", "number", "+(+)0."), "1\n")

	def test_countdown_subtracts_one_at_each_end_of_turn(self):
		self.assertEqual(self.run_script("countdown", "char", "++++++++[>+++++++++<]>."), "H")
		self.assertEqual(self.run_script("countdown", "number", "+++[>++<]>."), "6\n")
		self.assertEqual(self.run_script("countdown", "number", "[>+<]."), "0\n")
		self.assertEqual(self.run_script("countdown", "number", "++[>+++[>+<]<]>>."), "6\n")

	def test_repeat_runs_the_body_as_many_times_as_the_cell_when_it_starts(self):
		self.assertEqual(self.run_script("repeat", "char", "++++++++{>+++++++++<}>.+."), "HI")
		self.assertEqual(self.run_script("repeat", "number", "+++{>++<}>."), "6\n")
		self.assertEqual(self.run_script("repeat", "number", "{>+<}>+."), "1\n")
		# The cell is not counted down: the inner loop runs 3 times, then 6 times.
		self.assertEqual(self.run_script("repeat", "number", "++{>+++{>+<}<}>>."), "9\n")

	def test_bytes_wrap_and_other_characters_are_ignored(self):
		self.assertEqual(self.run_script("repeat", "number", "-."), "255\n")
		self.assertEqual(self.run_script("times", "number", "a+b+ c."), "2\n")
		self.assertEqual(self.run_script("repeat", "number", "(+++)[++]{.}"), "5\n" * 5)

	def test_not_one_argument_gives_a_newline(self):
		self.assertEqual(out(TAPE_SCRIPT, {"loop": "repeat", "print": "char"}), "\n")

class TestByteDump(unittest.TestCase):
	"""Bytes in hex, 8 or 12 per line, with their offset or their text."""

	def dump(self, layout, width, text):
		return out(BYTE_DUMP, {"layout": layout, "width": width}, text)

	def test_offset_layout(self):
		self.assertEqual(self.dump("offset", "eight", "Hello, 42!"),
			"0000: 48 65 6c 6c 6f 2c 20 34\n0008: 32 21\n")
		self.assertEqual(self.dump("offset", "twelve", "Hello, 42!"),
			"0000: 48 65 6c 6c 6f 2c 20 34 32 21\n")
		self.assertEqual(self.dump("offset", "eight", "abcdefghijklmnopq"),
			"0000: 61 62 63 64 65 66 67 68\n0008: 69 6a 6b 6c 6d 6e 6f 70\n0010: 71\n")
		self.assertEqual(self.dump("offset", "twelve", "abcdefghijklmnopq"),
			"0000: 61 62 63 64 65 66 67 68 69 6a 6b 6c\n000c: 6d 6e 6f 70 71\n")

	def test_text_layout_pads_the_last_line(self):
		self.assertEqual(self.dump("text", "eight", "Hello, 42!"),
			"48 65 6c 6c 6f 2c 20 34 |Hello, 4|\n32 21 " + " " * 18 + "|2!|\n")
		self.assertEqual(self.dump("text", "twelve", "Hello, 42!"),
			"48 65 6c 6c 6f 2c 20 34 32 21 " + " " * 6 + "|Hello, 42!|\n")

	def test_characters_that_cannot_be_printed_show_as_dots(self):
		self.assertEqual(self.dump("text", "eight", "a\tb\x7f"),
			"61 09 62 7f " + " " * 12 + "|a.b.|\n")

	def test_nothing_for_no_byte(self):
		self.assertEqual(self.dump("text", "twelve", ""), "")

class TestFlagMask(unittest.TestCase):
	"""Options from a to z, kept on or switched, shown three ways."""

	def flags(self, show, repeat, *args):
		return out(FLAG_MASK, {"show": show, "repeat": repeat}, *args)

	def test_options_set_once_stay_on(self):
		args = ("-ab", "-z", "x", "-a")
		self.assertEqual(self.flags("letters", "set", *args), "abz\n")
		self.assertEqual(self.flags("mask", "set", *args), "11" + "0" * 23 + "1\n")
		self.assertEqual(self.flags("hex", "set", *args), "2000003\n")

	def test_toggle_switches_an_option_each_time(self):
		args = ("-ab", "-z", "x", "-a")
		self.assertEqual(self.flags("letters", "toggle", *args), "bz\n")
		self.assertEqual(self.flags("mask", "toggle", *args), "01" + "0" * 23 + "1\n")
		self.assertEqual(self.flags("hex", "toggle", *args), "2000002\n")

	def test_a_bad_option_anywhere(self):
		self.assertEqual(self.flags("hex", "set", "-a1"), "Bad option\n")
		self.assertEqual(self.flags("letters", "toggle", "-b", "-A"), "Bad option\n")
		self.assertEqual(self.flags("mask", "set", "--a"), "Bad option\n")

	def test_no_option(self):
		self.assertEqual(self.flags("hex", "set"), "\n")
		self.assertEqual(self.flags("hex", "set", "-"), "0\n")
		self.assertEqual(self.flags("mask", "toggle", "word"), "0" * 26 + "\n")
		self.assertEqual(self.flags("letters", "set", "-aa", "-"), "a\n")
		self.assertEqual(self.flags("letters", "toggle", "-aa"), "\n")

class TestExprEval(unittest.TestCase):
	"""An expression in prefix, compact postfix or nested infix notation."""

	def calc(self, notation, *args):
		return out(EXPR_EVAL, {"notation": notation}, *args)

	def test_prefix(self):
		self.assertEqual(self.calc("prefix", "+ 3 4"), "7\n")
		self.assertEqual(self.calc("prefix", "* + 1 2 4"), "12\n")
		self.assertEqual(self.calc("prefix", "- 2 5"), "-3\n")
		self.assertEqual(self.calc("prefix", "/ -7 2"), "Error\n")
		self.assertEqual(self.calc("prefix", "  /  7 2 "), "3\n")
		self.assertEqual(self.calc("prefix", "42"), "42\n")
		for wrong in ("% 7 0", "+ 3", "3 4", "+ 3 4 5", "", "x", "+3 4"):
			self.assertEqual(self.calc("prefix", wrong), "Error\n", wrong)

	def test_compact_postfix(self):
		self.assertEqual(self.calc("compact", "34+2*"), "14\n")
		self.assertEqual(self.calc("compact", "25-"), "-3\n")
		self.assertEqual(self.calc("compact", "72/"), "3\n")
		self.assertEqual(self.calc("compact", "9"), "9\n")
		self.assertEqual(self.calc("compact", "05-3/"), "-1\n")
		self.assertEqual(self.calc("compact", "05-3%"), "-2\n")
		for wrong in ("70%", "3+", "34", "", "3 4+", "12"):
			self.assertEqual(self.calc("compact", wrong), "Error\n", wrong)

	def test_nested_infix(self):
		self.assertEqual(self.calc("nested", "((3+4)*2)"), "14\n")
		self.assertEqual(self.calc("nested", "(2-5)"), "-3\n")
		self.assertEqual(self.calc("nested", "((10/3)*3)"), "9\n")
		self.assertEqual(self.calc("nested", "42"), "42\n")
		for wrong in ("3+4", "((3+4)", "(3+4))", "(7%0)", "()", "(3 + 4)", "(3+)"):
			self.assertEqual(self.calc("nested", wrong), "Error\n", wrong)

	def test_not_one_argument_gives_a_newline(self):
		self.assertEqual(self.calc("prefix"), "\n")
		self.assertEqual(self.calc("nested", "1", "2"), "\n")

class TestSubjects(unittest.TestCase):
	def test_variant_counts_and_80_columns(self):
		counts = [(BOARD_THREAT, 8), (TAPE_SCRIPT, 6), (BYTE_DUMP, 4), (FLAG_MASK, 6), (EXPR_EVAL, 3)]
		for exercise, count in counts:
			combinations = exercise.combinations()
			self.assertEqual(len(combinations), count, exercise.name)
			for params in combinations:
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line), 80, f"{exercise.name} {params} : {line}")
