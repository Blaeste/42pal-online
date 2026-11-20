"""The exams: their settings in exams/<id>.json, and their levels.

The themes of a level come from themes.json, and the exercises of a theme
from the catalog. Like the rest of the core, this module never prints.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from pal42.catalog import load_catalog
from pal42.retry import RetryPolicy
from pal42.themes import load_themes
# Renamed here: Exam has its own draw(), for a whole level.
from pal42.variant import draw as draw_variant

# exams/ is at the root of the project, next to exercises/.
EXAMS_DIR = Path(__file__).resolve().parent.parent / "exams"

# The waits after a failed grademe, in minutes, when the exam file gives none.
# hard is 42_EXAM's: its exercise.cpp waits along a Fibonacci-like list.
DEFAULT_RETRY_MINUTES = {"soft": [0, 1, 2, 3, 5], "hard": [0.5, 2.5, 3, 5.5, 8.5, 14, 22.5, 36.5, 59]}

# Who an exam is for: the piscine, or the students of the cursus.
AUDIENCES = ("piscine", "student")

class ExamError(ValueError):
	"""An exam file is missing or badly written; the message says why."""

@dataclass(frozen=True)
class Exam:
	"""An exam: its settings, and the exercises of each level by theme.

	levels maps a level number to {theme id: exercises of that theme}, with
	only the themes that have exercises. warnings name the levels that have
	none yet; the front-ends show them.
	"""
	id: str
	title: str
	language: str
	level_count: int
	duration_minutes: int
	compile_command: tuple[str, ...]
	levels: dict
	warnings: list
	# {"soft": RetryPolicy, "hard": RetryPolicy}: the waits after a failure.
	retry: dict = field(default_factory=dict)
	# One of AUDIENCES: the menu first asks who the student is.
	audience: str = "student"

	@property
	def points_per_level(self):
		"""Points a passed level is worth, like 42_EXAM: 100 shared by the levels."""
		return 100 / self.level_count

	@property
	def playable_levels(self):
		"""The levels that have at least one exercise, in order."""
		return [level for level, themes in sorted(self.levels.items()) if themes]

	def exercises_at(self, level):
		"""Return the exercises that can be drawn at `level`."""
		return [exo for exercises in self.levels[level].values() for exo in exercises]

	def draw(self, level, rng):
		"""Draw a subject at `level`: a theme, then a model of it, then a seed.

		The theme comes first, so that each theme has the same chance, however
		many models it has. rng is a random.Random: the same one gives the same
		subject.
		"""
		# sorted: the same order on every machine, so the same draws.
		theme = rng.choice(sorted(self.levels[level]))
		exo = rng.choice(self.levels[level][theme])
		return draw_variant(exo, rng.randrange(2**31))

def load_exam(exam_id, exams_dir=EXAMS_DIR, catalog=None, themes=None):
	"""Load exams/<exam_id>.json and find the exercises of each level."""
	if themes is None:
		themes = load_themes()
	if catalog is None:
		catalog = load_catalog(themes=themes)
	path = exams_dir / f"{exam_id}.json"
	if not path.exists():
		raise ExamError(f"unknown exam '{exam_id}', choose among: {', '.join(list_exams(exams_dir))}")
	data = _read_exam_file(path)
	levels = {}
	for level in range(1, data["levels"] + 1):
		levels[level] = {}
		for theme in themes.values():
			if level in theme.exams.get(exam_id, ()):
				exercises = tuple(catalog.find(data["language"], theme.id))
				if exercises:
					levels[level][theme.id] = exercises
	warnings = [
		f"{data['title']}, level {level}: no exercise yet, the level cannot be played"
		for level, found in levels.items() if not found
	]
	retry = {mode: RetryPolicy(tuple(minutes)) for mode, minutes in data["retry_minutes"].items()}
	return Exam(
		exam_id, data["title"], data["language"], data["levels"],
		data["duration_minutes"], tuple(data["compile"]), levels, warnings, retry,
		audience=data["audience"],
	)

def list_exams(exams_dir=EXAMS_DIR):
	"""Return the ids of the exams that have a file in `exams_dir`, sorted."""
	return sorted(path.stem for path in exams_dir.glob("*.json"))

def _read_exam_file(path):
	"""Read an exam file and check its fields; raise ExamError if one is wrong."""
	def fail(reason):
		raise ExamError(f"{path.name}: {reason}")

	data = json.loads(path.read_text(encoding="utf-8"))
	for field in ("title", "audience", "language", "levels", "duration_minutes", "compile"):
		if field not in data:
			fail(f"the field '{field}' is missing")
	if data["audience"] not in AUDIENCES:
		fail(f"'audience' must be one of {', '.join(AUDIENCES)}, not {data['audience']!r}")
	for field in ("levels", "duration_minutes"):
		value = data[field]
		# bool is a kind of int in Python (True == 1): refuse it too.
		if isinstance(value, bool) or not isinstance(value, int) or value < 1:
			fail(f"'{field}' must be a positive integer, not {value!r}")
	if not data["compile"]:
		fail("'compile' is empty: it needs at least the name of the compiler")
	data.setdefault("retry_minutes", DEFAULT_RETRY_MINUTES)
	for mode in ("soft", "hard"):
		minutes = data["retry_minutes"].get(mode)
		if not minutes or any(
			isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0
			for value in minutes
		):
			fail(f"'retry_minutes' needs a '{mode}' list of minutes (numbers from 0), not {minutes!r}")
	return data
