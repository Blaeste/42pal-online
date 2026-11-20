"""Tests of pal42.progress: what the history and the grademe say of a student.

Run all the tests from the project root with: python3 -m unittest -v
"""

import io
import tempfile
import unittest
from pathlib import Path
from random import Random

import pal42.cli  # noqa: F401 (puts vendor/ on the path, for rich)
from rich.console import Console

from pal42.catalog import load_catalog
from pal42.cli.shell import Shell
from pal42.cli.workspace import Workspace
from pal42.exam import load_exam
from pal42.themes import load_themes
from tests.test_cli import ECHO_CATALOG, ECHO_THEMES, Script

from pal42.progress import exam_rows, summary, weak_themes
from pal42.session import SessionStore

def grade(variant, themes, passed, source="rank02"):
	return {"variant": variant, "themes": themes, "passed": passed, "source": source}

GRADES = [
	grade("shift_letters#1", ["letter_rotation"], False),
	grade("shift_letters#1", ["letter_rotation"], True),
	grade("word_pick#2", ["find_word"], False),
	grade("word_pick#2", ["find_word"], False),
	grade("word_each#3", ["find_word"], True, source="practice"),
	grade("bip_bop#4", ["number_words"], True),
	grade("case_flip#5", ["case_swap"], False),
]

HISTORY = [
	{"exam": "rank02", "title": "Exam Rank 02", "grade": 50, "end": "finish"},
	{"exam": "rank02", "title": "Exam Rank 02", "grade": 100.00000000000001, "end": "passed", "cheat": True},
	{"exam": "rank02", "title": "Exam Rank 02", "grade": 75, "end": "time"},
	{"exam": "piscine_01", "title": "Piscine Exam 01", "grade": 25, "end": "abandoned"},
]

class TestStore(unittest.TestCase):
	def test_each_grademe_is_kept_in_order(self):
		with tempfile.TemporaryDirectory() as tmp:
			store = SessionStore(Path(tmp))
			self.assertEqual(store.grades(), [])
			store.add_grade(GRADES[0])
			store.add_grade(GRADES[1])
			self.assertEqual(store.grades(), GRADES[:2])

class TestProgress(unittest.TestCase):
	def test_the_weakest_themes_first(self):
		"""find_word: 1 OK in 3; case_swap: 0 in 1; letter_rotation: 1 in 2; number_words: all OK."""
		rows = weak_themes(GRADES)
		self.assertEqual([row.theme for row in rows], ["case_swap", "find_word", "letter_rotation"])
		self.assertEqual((rows[1].tries, rows[1].oks), (3, 1))

	def test_each_exam_with_its_best_grade_cheats_left_out(self):
		rows = exam_rows(HISTORY)
		self.assertEqual([(row.title, row.tries, row.passed, row.best) for row in rows],
			[("Exam Rank 02", 2, 0, 75), ("Piscine Exam 01", 1, 0, 25)])

	def test_the_summary_line(self):
		self.assertEqual(summary(HISTORY, GRADES), "3 exams · 7 grademe · 3 OK (43%) · best 75/100, Exam Rank 02")
		self.assertEqual(summary([], []), "No grademe yet")

class TestShellProgress(unittest.TestCase):
	"""Each grademe is kept; the first menu offers Progress once there is one."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.store = SessionStore(Path(self.tmp.name) / "state")

	def tearDown(self):
		self.tmp.cleanup()

	def shell(self, *answers, catalog=ECHO_CATALOG, themes=ECHO_THEMES):
		self.script = Script(*answers)
		console = Console(file=io.StringIO(), width=100, color_system=None)
		return Shell(console, self.script.ask, lambda prompt: "pw", Workspace(Path(self.tmp.name) / "exam"),
			rng=Random(1), sleep=lambda seconds: None, store=self.store, catalog=catalog, themes=themes)

	def test_a_grademe_is_kept_with_its_themes(self):
		shell = self.shell()
		shell.start(load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES), 2)
		shell.handle("grademe")
		entry = self.store.grades()[-1]
		self.assertEqual((entry["variant"], entry["themes"], entry["passed"], entry["source"]),
			(shell.variant.id, ["char_sets"], False, "rank02"))

	def test_progress_shows_the_weak_themes_and_practises_one(self):
		"""The real catalog: Progress (3rd choice), then the weakest theme: a practice subject on it."""
		themes = load_themes()
		catalog = load_catalog(themes=themes)
		for passed in (False, False, True):
			self.store.add_grade(grade("word_pick#2", ["find_word"], passed))
		self.store.add_grade(grade("bip_bop#4", ["number_words"], True))
		shell = self.shell("", "pw", "4", "1", "finish", catalog=catalog, themes=themes)
		shell.run()
		text = shell.console.file.getvalue()
		self.assertRegex(text, r"4\. Progress +your exams and weak themes")
		self.assertIn("4 grademe · 2 OK (50%)", text)
		self.assertRegex(text, r"1\. find_word +1 OK out of 3 grademe")
		self.assertIn("Practice summary", text)

	def test_no_grademe_no_progress_in_the_menu(self):
		shell = self.shell("", "pw", "3", catalog=load_catalog(), themes=load_themes())
		shell.run()
		self.assertNotIn("Progress", shell.console.file.getvalue())
