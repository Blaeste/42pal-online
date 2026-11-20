"""Tests of the byte_rotate exercise (a function on the bits of a byte).

The test main prints the byte the function returns, in binary. The
expected outputs below are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.model import TestCase
from pal42.subject import render
from pal42.variant import Variant

EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/byte_rotate/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(byte, way, amount, invert="keep"):
	"""What the test main prints: the byte returned, in binary."""
	params = {"way": way, "amount": amount, "invert": invert}
	return EXERCISE.oracle(params, TestCase((str(byte),)))

class TestOracle(unittest.TestCase):
	"""What ft_rotate_<way>_<amount>_<invert> must return, worked out by hand."""

	def test_rotations_bring_the_lost_bits_back_on_the_other_side(self):
		"""10000001 left 1: 00000011; 00000110 right 2: 10000001."""
		self.assertEqual(output(129, "left", "1"), "00000011\n")
		self.assertEqual(output(6, "right", "2"), "10000001\n")
		self.assertEqual(output(255, "left", "3"), "11111111\n")

	def test_flip_inverts_every_bit_after_the_rotation(self):
		"""38 = 00100110, left 3: 00110001, flipped: 11001110."""
		self.assertEqual(output(38, "left", "3", "flip"), "11001110\n")
		self.assertEqual(output(0, "right", "1", "flip"), "11111111\n")

class TestVariants(unittest.TestCase):
	"""The variants of byte_rotate."""

	def test_twelve_variants_with_examples_within_80_columns(self):
		"""2 ways x 3 amounts x 2 inversions; each call shows the byte in binary."""
		combinations = EXERCISE.combinations()
		self.assertEqual(len(combinations), 12)
		for params in combinations:
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"{variant.name}(38) /* 00100110 */", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_no_rotation_by_four(self):
		"""Rotating by 4 swaps the two halves of the byte: a real subject, left out."""
		self.assertNotIn("4", EXERCISE.params[1].values)

	def test_generated_tests_are_reproducible_with_the_patterns(self):
		"""Same seed, same tests; 0, 255 and 10101010 are in."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		for byte in ["0", "255", "170"]:
			self.assertIn(TestCase((byte,)), tests)
