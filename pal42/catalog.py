"""The catalog: every exercise found in exercises/, indexed for the draws.

Each exercise lives in its own folder, exercises/<language>/<name>/, whose
exercise.py defines EXERCISE. Like the rest of the core, this module never
prints.
"""

from dataclasses import dataclass, field
from pathlib import Path
from runpy import run_path

from pal42.model import Exercise
from pal42.themes import load_themes
from pal42.variant import draw

# exercises/ is next to the pal42 package, at the root of the project.
EXERCISES_DIR = Path(__file__).resolve().parent.parent / "exercises"

@dataclass
class Catalog:
	"""The exercises found, by name, and the warnings about skipped folders.

	The front-ends show the warnings: the core itself never prints.
	folders gives the folder of each exercise, which also holds its ref.c.
	"""
	exercises: dict[str, Exercise]
	warnings: list[str]
	folders: dict[str, Path] = field(default_factory=dict)

	def find(self, language, theme):
		"""Return the exercises of `language` that train `theme`."""
		return [
			exo for exo in self.exercises.values()
			if exo.language == language and theme in exo.themes
		]

	def variant(self, variant_id):
		"""Return the variant named `variant_id` (exo#seed), or None if unknown.

		The same exercise and seed give the same variant: that is how a saved
		exam finds its subject again.
		"""
		name, _, seed = variant_id.partition("#")
		if name not in self.exercises or not seed.isdigit():
			return None
		return draw(self.exercises[name], int(seed))

class SkippedFolder(Exception):
	"""A folder of exercises/ that gives no exercise; the message says why."""

def load_catalog(root=EXERCISES_DIR, themes=None):
	"""Find and load every exercise under `root`.

	A folder that cannot give an exercise is skipped with a warning, so that
	one broken exercise does not stop the others from being used.
	themes are the known themes, by id; None means those of themes.json.
	"""
	if themes is None:
		themes = load_themes()
	exercises = {}
	warnings = []
	# The folder each name was found in, like "c/char_filter", and its path.
	found_in = {}
	folders = {}
	# sorted: the same order on every machine, whatever the file system says.
	for folder in sorted(path for path in root.glob("*/*") if path.is_dir()):
		# Shown as "c/char_filter" in the warnings.
		where = folder.relative_to(root).as_posix()
		try:
			exo = _load_exercise(folder)
			unknown = [theme for theme in exo.themes if theme not in themes]
			if unknown:
				raise SkippedFolder(f"unknown theme '{', '.join(unknown)}'")
			# The name identifies the exercise (exo#seed): it must be unique.
			if exo.name in found_in:
				raise SkippedFolder(
					f"the name '{exo.name}' is already taken by {found_in[exo.name]}"
				)
		except SkippedFolder as reason:
			warnings.append(f"{where}: {reason}, folder skipped")
			continue
		exercises[exo.name] = exo
		found_in[exo.name] = where
		folders[exo.name] = folder
	return Catalog(exercises, warnings, folders)

def _load_exercise(folder):
	"""Return the EXERCISE defined by folder/exercise.py, or raise SkippedFolder."""
	file = folder / "exercise.py"
	if not file.exists():
		raise SkippedFolder("no exercise.py")
	try:
		# run_path runs exercise.py and returns its global names.
		names = run_path(str(file))
	# Any error: an ExerciseError from the model, but also a typo
	# (SyntaxError, NameError...) in a file written by a contributor.
	except Exception as error:
		raise SkippedFolder(f"exercise.py refused ({error})") from error
	if "EXERCISE" not in names:
		raise SkippedFolder("no EXERCISE in exercise.py")
	return names["EXERCISE"]
