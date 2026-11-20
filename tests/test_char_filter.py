"""Tests of the char_filter exercise: its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle:
that is what checks the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

# run_path runs exercise.py and returns its global names, EXERCISE among them.
EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/char_filter/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

# Our own example arguments, also shown in the subject.
PROGRAMMING = ("programming", "gaming")
MULHOUSE = ("mulhouse", "house42")

def output(args, mode, order="appearance", separator="none"):
	"""What the oracle says the program prints for these arguments and params."""
	params = {"mode": mode, "order": order, "separator": separator}
	return EXERCISE.oracle(params, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What char_filter must print, worked out by hand."""

	def test_common_characters(self):
		"""common: the characters found in both strings, each one once."""
		# programming / gaming: g a m i n are in both; r, m and g repeat in s1.
		self.assertEqual(output(PROGRAMMING, "common"), "gamin\n")
		# mulhouse / house42: u h o s e are in both; u repeats in s1.
		self.assertEqual(output(MULHOUSE, "common"), "uhose\n")

	def test_characters_only_in_first(self):
		"""only_first: the characters of s1 that never appear in s2."""
		# programming / gaming: p r o are not in gaming.
		self.assertEqual(output(PROGRAMMING, "only_first"), "pro\n")
		# mulhouse / house42: m l are not in house42.
		self.assertEqual(output(MULHOUSE, "only_first"), "ml\n")

	def test_characters_only_in_second(self):
		"""only_second: the characters of s2 that never appear in s1."""
		# mulhouse / house42: 4 and 2 are not in mulhouse.
		self.assertEqual(output(MULHOUSE, "only_second"), "42\n")
		# programming / gaming: every letter of gaming is in programming,
		# so the set is empty and only the newline is printed.
		self.assertEqual(output(PROGRAMMING, "only_second"), "\n")

	def test_ascii_order(self):
		"""ascii: the same characters, sorted by increasing ASCII value."""
		# u h o s e sorted: e h o s u.
		self.assertEqual(output(MULHOUSE, "common", order="ascii"), "ehosu\n")
		# p r o sorted: o p r.
		self.assertEqual(output(PROGRAMMING, "only_first", order="ascii"), "opr\n")
		# 4 2 sorted: '2' (50) comes before '4' (52).
		self.assertEqual(output(MULHOUSE, "only_second", order="ascii"), "24\n")

	def test_space_separator(self):
		"""space: one space between the characters, none at the ends."""
		self.assertEqual(output(PROGRAMMING, "common", separator="space"), "g a m i n\n")
		self.assertEqual(
			output(MULHOUSE, "only_first", order="ascii", separator="space"), "l m\n"
		)
		# An empty set stays an empty line: no stray space.
		self.assertEqual(output(PROGRAMMING, "only_second", separator="space"), "\n")

	def test_wrong_number_of_arguments_prints_only_a_newline(self):
		"""With 0, 1 or 3 arguments, every variant prints only a newline."""
		for args in [(), ("programming",), ("a", "b", "c")]:
			for mode in ["common", "only_first", "only_second"]:
				self.assertEqual(output(args, mode, separator="space"), "\n", args)

class TestVariants(unittest.TestCase):
	"""The variants that can be drawn from char_filter."""

	def test_real_subject_combination_is_never_drawn(self):
		"""common + appearance + none gives back the real subject: never drawn."""
		real_subject = {"mode": "common", "order": "appearance", "separator": "none"}
		self.assertNotIn(real_subject, EXERCISE.combinations())
		# 3 modes x 2 orders x 2 separators, minus the real subject.
		self.assertEqual(len(EXERCISE.combinations()), 11)

	def test_generated_tests_are_reproducible_and_cover_edge_cases(self):
		"""Same seed, same tests; wrong argument counts and empty strings are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertTrue(any(len(test.args) != 2 for test in tests), "no test with a wrong number of arguments")
		self.assertIn(TestCase(("", "")), tests)
		self.assertGreaterEqual(len(tests), 10)

	def test_every_variant_has_a_subject_within_80_columns(self):
		"""The subject of each of the 11 variants is written, lines of 80 at most."""
		for params in EXERCISE.combinations():
			subject = render(Variant(EXERCISE, 0, params))
			self.assertIn("Examples:", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
