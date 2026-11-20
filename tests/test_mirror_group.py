"""Tests of the mirror_group exercise (a program): its oracle and its variants.

The expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/mirror_group/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(args, group, case="keep"):
	return EXERCISE.oracle({"group": group, "case": case}, TestCase(args))

class TestOracle(unittest.TestCase):
	"""What mirror_<group>_<case> must print, worked out by hand."""

	def test_each_group(self):
		"""e<->o; b<->z, c<->y, x<->d; 1<->8, 9<->0; a<->m, n<->z."""
		self.assertEqual(output(("Hello World",), "vowels"), "Holle Werld\n")
		self.assertEqual(output(("abc xyz",), "consonants"), "azy dcb\n")
		self.assertEqual(output(("a1b9",), "digits"), "a8b0\n")
		self.assertEqual(output(("amnz",), "halves"), "mazn\n")

	def test_the_middle_of_a_group_stays(self):
		"""i is the middle vowel, n the middle consonant, g and t the middles of the halves."""
		self.assertEqual(output(("in",), "vowels"), "in\n")
		self.assertEqual(output(("n",), "consonants"), "n\n")
		self.assertEqual(output(("gt",), "halves"), "gt\n")

	def test_swap_changes_the_case_of_the_group(self):
		"""A->M then m; b->l then L; the space is not in the group."""
		self.assertEqual(output(("Ab c",), "halves", "swap"), "mL K\n")

	def test_not_one_argument_gives_a_newline(self):
		for args in [(), ("a", "b")]:
			self.assertEqual(output(args, "digits"), "\n", args)

class TestVariants(unittest.TestCase):
	def test_seven_variants_within_80_columns(self):
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 7)
		for params in combinations:
			for line in render(Variant(EXERCISE, 0, params)).splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")
