"""Tests of pal42.variant: drawing a variant of an exercise from a seed.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest

from pal42.model import Param
from pal42.variant import Variant, draw
from tests.helpers import make_exercise

# Enough seeds for every value to come out, as the plan asks (step 3).
SEEDS = range(200)

def make_two_param_exercise(**changes):
	"""An exercise with 3 x 2 = 6 combinations of params, to draw from."""
	fields = dict(
		params=(
			Param("mode", ("common", "only_first", "only_second")),
			Param("order", ("first", "second")),
		),
		subject="Display the characters $mode, in the order of the $order string.",
	)
	fields.update(changes)
	return make_exercise(**fields)

class TestDraw(unittest.TestCase):
	"""draw(exo, seed) picks one value for each param of the exercise."""

	def test_variant_id_is_exercise_hash_seed(self):
		"""A variant is identified by `exo#seed`, enough to draw it again."""
		self.assertEqual(draw(make_exercise(), 42).id, "char_filter#42")

	def test_name_depends_on_params(self):
		"""The holes of assignment_name are filled with the drawn values."""
		exo = make_two_param_exercise(assignment_name="${mode}_chars")
		for seed in range(10):
			variant = draw(exo, seed)
			self.assertEqual(variant.name, variant.params["mode"] + "_chars")

	def test_expected_files_depend_on_params(self):
		"""The holes of expected_files are filled like the name, so they match it."""
		exo = make_two_param_exercise(
			assignment_name="${mode}_chars", expected_files=("${mode}_chars.c",)
		)
		for seed in range(10):
			variant = draw(exo, seed)
			self.assertEqual(variant.expected_files, (variant.name + ".c",))

	def test_defines_give_one_flag_per_param_for_the_reference(self):
		"""-D<PARAM>_<VALUE> in capitals: ref.c tests them with #if defined(...)."""
		variant = Variant(make_two_param_exercise(), 0, {"mode": "only_first", "order": "second"})
		self.assertEqual(variant.defines, ("-DMODE_ONLY_FIRST", "-DORDER_SECOND"))

	def test_name_defaults_to_exercise_name(self):
		"""Without assignment_name, the student sees the exercise name."""
		self.assertEqual(draw(make_exercise(), 42).name, "char_filter")

	def test_same_seed_gives_same_variant(self):
		"""A variant is reproducible: drawing twice with one seed gives the same."""
		exo = make_two_param_exercise()
		self.assertEqual(draw(exo, 42).params, draw(exo, 42).params)

	def test_every_value_is_drawn(self):
		"""Over 200 seeds, each value of each param comes out at least once."""
		exo = make_two_param_exercise()
		variants = [draw(exo, seed) for seed in SEEDS]
		for param in exo.params:
			drawn = {variant.params[param.name] for variant in variants}
			self.assertEqual(drawn, set(param.values), param.name)

	def test_forbidden_combination_is_never_drawn(self):
		"""Over 200 seeds, the forbidden combination never comes out."""
		forbidden = {"mode": "common", "order": "first"}
		exo = make_two_param_exercise(forbidden=(forbidden,))
		for seed in SEEDS:
			self.assertNotEqual(draw(exo, seed).params, forbidden, f"seed {seed}")

	def test_forbidden_combination_on_some_params_only(self):
		"""Forbidding mode + order forbids them whatever the other params are."""
		exo = make_two_param_exercise(
			params=(
				Param("mode", ("common", "only_first", "only_second")),
				Param("order", ("first", "second")),
				Param("sep", ("none", "space")),
			),
			forbidden=({"mode": "common", "order": "first"},),
		)
		for seed in SEEDS:
			params = draw(exo, seed).params
			self.assertFalse(
				params["mode"] == "common" and params["order"] == "first",
				f"seed {seed} : {params}",
			)
