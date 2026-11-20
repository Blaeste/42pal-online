"""Tests of the name_style exercise (a program): its oracle and its variants.

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

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/name_style/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, source, target):
	"""What <source>_to_<target> prints for these arguments."""
	return EXERCISE.oracle({"source": source, "target": target}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What <source>_to_<target> must print, worked out by hand."""

	def test_the_same_three_words_in_every_style(self):
		"""big red box, from one style to another."""
		self.assertEqual(output(("big_red_box",), "snake", "kebab"), "big-red-box\n")
		self.assertEqual(output(("big-red-box",), "kebab", "pascal"), "BigRedBox\n")
		self.assertEqual(output(("bigRedBox",), "camel", "constant"), "BIG_RED_BOX\n")
		self.assertEqual(output(("BigRedBox",), "pascal", "camel"), "bigRedBox\n")
		self.assertEqual(output(("BIG_RED_BOX",), "constant", "kebab"), "big-red-box\n")

	def test_one_letter_words_and_one_word(self):
		"""In ABC, each capital starts a word: a, b, c."""
		self.assertEqual(output(("ABC",), "pascal", "snake"), "a_b_c\n")
		self.assertEqual(output(("a-b-c",), "kebab", "camel"), "aBC\n")
		self.assertEqual(output(("hello",), "snake", "pascal"), "Hello\n")
		self.assertEqual(output(("HELLO",), "constant", "camel"), "hello\n")

	def test_empty_string_or_not_one_argument_gives_a_newline(self):
		"""No word, no argument, or two arguments."""
		for args in [("",), (), ("big_box", "red")]:
			self.assertEqual(output(args, "snake", "kebab"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants of name_style."""

	def test_eighteen_variants_without_the_real_subjects(self):
		"""5 x 5 styles, without a style into itself, camel_to_snake and snake_to_camel."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 18)
		names = {Variant(EXERCISE, 0, params).name for params in combinations}
		for name in ["camel_to_snake", "snake_to_camel", "kebab_to_kebab"]:
			self.assertNotIn(name, names)
		self.assertIn("pascal_to_kebab", names)

	def test_the_examples_are_written_in_the_source_style(self):
		"""kebab_to_pascal shows big-red-box; constant_to_camel shows BIG_RED_BOX."""
		subject = render(Variant(EXERCISE, 0, {"source": "kebab", "target": "pascal"}))
		self.assertIn("$>./kebab_to_pascal big-red-box | cat -e\nBigRedBox$", subject)
		subject = render(Variant(EXERCISE, 0, {"source": "constant", "target": "camel"}))
		self.assertIn("$>./constant_to_camel BIG_RED_BOX | cat -e\nbigRedBox$", subject)

	def test_subjects_within_80_columns(self):
		"""Every variant, with its two style texts."""
		for params in EXERCISE.combinations():
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_generated_names_are_written_in_the_source_style(self):
		"""Same seed, same tests; for pascal, each name starts with an uppercase letter."""
		params = {"source": "pascal", "target": "kebab"}
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertIn(TestCase(("TheQuickBrownFoxJumps",)), tests)
		for test in tests[3:]:
			self.assertTrue(test.args[0][0].isupper(), test)
