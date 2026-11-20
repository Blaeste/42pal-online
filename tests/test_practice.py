"""Tests of pal42.practice: drawing subjects to practise one theme.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from random import Random

from pal42.catalog import load_catalog
from pal42.practice import draw_practice

class TestDrawPractice(unittest.TestCase):
	"""draw_practice(exercises, rng, seen): a new subject of the theme."""

	def test_five_draws_give_five_seeds_of_the_same_theme(self):
		"""Each draw is an exercise of the theme, with a seed not seen before."""
		exercises = load_catalog().find("c", "common_chars")
		seen = set()
		for _ in range(5):
			variant = draw_practice(exercises, Random(1), seen)
			self.assertIn("common_chars", variant.exercise.themes)
			self.assertNotIn(variant.id, seen)
			seen.add(variant.id)
		self.assertEqual(len(seen), 5)
