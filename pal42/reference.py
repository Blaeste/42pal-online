"""Checking the catalog: each reference solution must pass its own exercise.

The reference solution is ref.c for a C exercise, ref.py for a Python one.
If the oracle and the reference, written separately, disagree on a test,
one of them is wrong: that is how the grading itself is checked. Like the
rest of the core, this module never prints.
"""

import shutil
import tempfile
import traceback
from pathlib import Path

from pal42.grader import Grade, grade
from pal42.runners import runner_for
from pal42.runners.c import DEFAULT_COMMAND
from pal42.variant import draw

# The reference solution of an exercise, in its folder, by language.
REFERENCE_FILES = {"c": "ref.c", "python": "ref.py"}

# Past this many combinations, check-catalog grades this many variants only.
MAX_VARIANTS = 50

def variants_to_check(exo, max_variants=MAX_VARIANTS):
	"""Return the variants of `exo` to grade: each combination once.

	They are drawn like at the exam, with the seeds 0, 1, 2..., so that a
	failure named exo#seed can be drawn again exactly. With more than
	max_variants combinations, only the first max_variants seeds are taken.
	"""
	if len(exo.combinations()) > max_variants:
		return [draw(exo, seed) for seed in range(max_variants)]
	found = {}
	seed = 0
	while len(found) < len(exo.combinations()):
		variant = draw(exo, seed)
		# A dict is not hashable: its sorted pairs stand for the combination.
		found.setdefault(tuple(sorted(variant.params.items())), variant)
		seed += 1
	return list(found.values())

def reference_path(exo, folder):
	"""The reference solution of `exo` in its folder: ref.c, or ref.py for Python."""
	return Path(folder) / REFERENCE_FILES[exo.language]

def reference_files(variant, ref):
	"""Return where each expected file of `variant` comes from: {name: path}.

	ref.c stands for the first expected file. The other ones, like a header
	the student hands in too, are the files of the same name next to ref.c.
	"""
	ref = Path(ref)
	sources = {variant.expected_files[0]: ref}
	for name in variant.expected_files[1:]:
		sources[name] = ref.parent / name
	return sources

def check_variant(variant, ref):
	"""Grade the reference solution `ref` (a ref.c) for `variant`; return the Grade.

	ref.c, and the other expected files next to it, are put in a temporary
	rendu under the expected names, then graded like a student's work,
	compiled with the -D flags of the variant: it must call no forbidden
	function and pass every test of the oracle. A file missing next to ref.c
	is missing from the rendu: the grade says so. A ref.py defines the
	functions of all the variants, under their names: no flags needed.
	"""
	with tempfile.TemporaryDirectory() as rendu:
		for name, source in reference_files(variant, ref).items():
			if source.is_file():
				shutil.copy(source, Path(rendu) / name)
		if variant.exercise.language == "c":
			runner = runner_for("c", DEFAULT_COMMAND + variant.defines)
		else:
			runner = runner_for(variant.exercise.language)
		try:
			return grade(variant, rendu, runner)
		# The oracle or the generator of the exercise failed: said, so that the
		# other variants and exercises are still checked.
		except Exception as error:
			trace = "".join(traceback.format_exception_only(type(error), error))
			return Grade(False, f"The exercise itself failed:\n{trace}", 0, 0)
