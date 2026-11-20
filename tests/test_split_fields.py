"""Tests of the split_fields exercise (a function): its oracle and its variants.

The test main prints each field between brackets, one per line, so that an
empty field shows as []. The expected outputs are worked out by hand.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/split_fields/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, separator, empty="skip"):
	"""What the test main prints for the fields of `text`."""
	return EXERCISE.oracle({"separator": separator, "empty": empty}, TestCase((text,)))

class TestOracle(unittest.TestCase):
	"""What ft_split_<separator>_<empty> must return, worked out by hand."""

	def test_skip_leaves_out_the_empty_fields(self):
		"""skip: two separators in a row, or at an end, give no empty field."""
		self.assertEqual(output("a,,b", "comma"), "[a]\n[b]\n")
		self.assertEqual(output(",a,", "comma"), "[a]\n")
		self.assertEqual(output("x:y", "colon"), "[x]\n[y]\n")
		# Not its separator: a comma is a plain character for colon.
		self.assertEqual(output("a,b", "colon"), "[a,b]\n")
		# No field at all: nothing is printed.
		self.assertEqual(output("", "semicolon"), "")

	def test_keep_gives_an_empty_field_between_two_separators(self):
		"""keep: n separators always give n + 1 fields, some of them empty."""
		self.assertEqual(output("a,,b", "comma", "keep"), "[a]\n[]\n[b]\n")
		self.assertEqual(output(",a,", "comma", "keep"), "[]\n[a]\n[]\n")
		self.assertEqual(output("a;b;", "semicolon", "keep"), "[a]\n[b]\n[]\n")
		# An empty string is one empty field.
		self.assertEqual(output("", "colon", "keep"), "[]\n")

	def test_whitespace_cuts_at_each_space_tab_and_newline(self):
		"""whitespace: space, tab and newline are all separators, one by one."""
		self.assertEqual(output("a\tb\nc", "whitespace", "keep"), "[a]\n[b]\n[c]\n")
		self.assertEqual(output("a  b", "whitespace", "keep"), "[a]\n[]\n[b]\n")

class TestVariants(unittest.TestCase):
	"""The variants of split_fields."""

	def test_generated_tests_start_with_the_edge_cases(self):
		"""Same seed, same tests; the first ones (checked by valgrind) are edge cases."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertGreaterEqual(len(tests), 10)
		self.assertEqual(tests[0], TestCase(("",)))
		self.assertTrue(all(len(test.args) == 1 for test in tests))

	def test_every_variant_has_a_subject_with_its_prototype(self):
		"""4 separators x 2, minus the real subject: 7 subjects within 80 columns."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 7)
		self.assertNotIn({"separator": "whitespace", "empty": "skip"}, combinations)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"char\t**{variant.name}(char *str);", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_the_subject_has_examples_written_as_calls(self):
		"""ft_split_comma_keep("a,,b") shows its three fields, one per line."""
		subject = render(Variant(EXERCISE, 0, {"separator": "comma", "empty": "keep"}))
		self.assertIn('ft_split_comma_keep("a,,b")\n[a]$\n[]$\n[b]$\n', subject)
		self.assertIn("between brackets", subject)
