"""Drawing a variant: one value for each param of an exercise, from a seed.

A variant is reproducible: the same exercise and the same seed always give
the same variant, so `exo#seed` is enough to find it again.
"""

import random
from dataclasses import dataclass
from string import Template

from pal42.model import Exercise

@dataclass(frozen=True)
class Variant:
	"""One variant of an exercise: the values drawn for its params."""
	exercise: Exercise
	seed: int
	params: dict[str, str]

	@property
	def id(self):
		"""`exo#seed`, like "char_filter#42": enough to draw this variant again."""
		return f"{self.exercise.name}#{self.seed}"

	@property
	def name(self):
		"""Assignment name of this variant: its holes filled with the drawn values."""
		template = self.exercise.assignment_name or self.exercise.name
		return Template(template).substitute(self.params)

	@property
	def expected_files(self):
		"""Files the student must hand in, holes filled like the name."""
		return tuple(
			Template(file).substitute(self.params)
			for file in self.exercise.expected_files
		)

	@property
	def defines(self):
		"""The -D flags that make ref.c this variant: -D<PARAM>_<VALUE>, in capitals.

		ref.c chooses its code with #if defined(MODE_COMMON) and the like.
		"""
		return tuple(
			f"-D{name.upper()}_{value.upper()}" for name, value in self.params.items()
		)

	@property
	def provided_files(self):
		"""The files given by the exercise, {name: content}, holes filled like the name."""
		return {
			name: Template(content).substitute(self.params)
			for name, content in self.exercise.provided_files.items()
		}

	@property
	def examples(self):
		"""The tests shown in the subject: fixed, or given by examples(params)."""
		if callable(self.exercise.examples):
			return tuple(self.exercise.examples(self.params))
		return self.exercise.examples

	@property
	def harness(self):
		"""C source of the test main of a function exercise, holes filled like the name."""
		return Template(self.exercise.harness).substitute(self.params)

def draw(exo, seed):
	"""Draw the variant of `exo` given by `seed`.

	It is picked among the allowed combinations only: no forbidden one can
	come out, and there is no draw-again loop that could never end.
	"""
	# A private Random seeded with `seed`: same seed, same draws, and the
	# global random module stays untouched.
	rng = random.Random(seed)
	params = rng.choice(exo.combinations())
	return Variant(exo, seed, params)
