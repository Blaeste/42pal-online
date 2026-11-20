"""The themes: the skills the exams test, listed in themes.json.

An exam level points to themes, and each exercise trains one or more themes.
A theme is described in our own words, never by a real subject.
"""

import json
from dataclasses import dataclass
from pathlib import Path

# themes.json is at the root of the project, next to exercises/.
THEMES_FILE = Path(__file__).resolve().parent.parent / "themes.json"

class ThemesError(ValueError):
	"""themes.json is badly written; the message says which theme and why."""

@dataclass(frozen=True)
class Theme:
	"""A theme: the skill it trains, and the exam levels where it appears.

	exams maps an exam to its levels, like {"rank02": (2, 3)}.
	"""
	id: str
	skill: str
	exams: dict[str, tuple[int, ...]]

def load_themes(path=THEMES_FILE):
	"""Return the themes of `path`, by id; raise ThemesError if one is wrong."""
	# object_pairs_hook is called for each {...} of the file, with its pairs
	# in order: it sees a key written twice, which json would silently drop.
	data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_twice)
	return {theme_id: _make_theme(theme_id, entry) for theme_id, entry in data.items()}

def _no_twice(pairs):
	"""Build a dict from the (key, value) pairs of one {...}, refusing doubles."""
	keys = [key for key, value in pairs]
	for key in keys:
		if keys.count(key) > 1:
			raise ThemesError(f"themes.json: '{key}' is written twice")
	return dict(pairs)

def _make_theme(theme_id, entry):
	"""Check one entry of themes.json and return its Theme."""
	# A function defined inside another one sees its variables: fail()
	# knows theme_id without being given it.
	def fail(reason):
		raise ThemesError(f"themes.json: theme '{theme_id}': {reason}")

	if not entry.get("skill"):
		fail("the skill is missing")
	if not entry.get("exams"):
		fail("it appears in no exam (exams)")
	for exam, levels in entry["exams"].items():
		if not levels:
			fail(f"no level for the exam '{exam}'")
		for level in levels:
			# bool is a kind of int in Python (True == 1): refuse it too.
			if isinstance(level, bool) or not isinstance(level, int):
				fail(f"the level {level!r} of '{exam}' is not an integer")
			if level < 1:
				fail(f"the level {level} of '{exam}' is not valid: levels start at 1")
	exams = {exam: tuple(levels) for exam, levels in entry["exams"].items()}
	return Theme(theme_id, entry["skill"], exams)
