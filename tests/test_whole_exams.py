"""Every exam, played from its first level to the end: it must reach 100/100.

At each level, the shell draws a subject like at the real exam; the test
hands in the reference solution of that subject, as a student would hand in
a right rendu, then types grademe. The exam must go up level by level and
end passed, kept in the history. This checks together the levels of the
exams, the draw, the subjects written, the grading and the end of an exam.

Run all the tests from the project root with: python3 -m unittest -v
"""

import io
import shutil
import tempfile
import unittest
from pathlib import Path
from random import Random

import pal42.cli  # noqa: F401 (puts vendor/ on the path, for rich)
from rich.console import Console

from pal42.catalog import load_catalog
from pal42.cli.shell import Shell
from pal42.cli.workspace import Workspace
from pal42.exam import list_exams, load_exam
from pal42.reference import reference_files, reference_path
from pal42.session import SessionStore
from pal42.themes import load_themes

THEMES = load_themes()
CATALOG = load_catalog(themes=THEMES)

def hand_in(shell):
	"""Write the reference solution of the current subject in its rendu folder.

	A ref.c chooses its variant with -D flags, which the student's compile
	command does not have: they become #define lines on top of the copy.
	"""
	variant = shell.variant
	exo = variant.exercise
	rendu = shell.workspace.rendu / variant.name
	rendu.mkdir(parents=True, exist_ok=True)
	sources = reference_files(variant, reference_path(exo, CATALOG.folders[exo.name]))
	for index, (name, source) in enumerate(sources.items()):
		if index == 0 and exo.language == "c":
			defines = "".join(f"#define {flag[2:]}\n" for flag in variant.defines)
			(rendu / name).write_text(defines + source.read_text(encoding="utf-8"), encoding="utf-8")
		else:
			shutil.copy(source, rendu / name)

class TestWholeExams(unittest.TestCase):
	"""Each exam of exams/, passed with the reference solutions."""

	def test_every_exam_can_be_passed_level_by_level(self):
		for exam_id in list_exams():
			with self.subTest(exam_id), tempfile.TemporaryDirectory() as tmp:
				exam = load_exam(exam_id, catalog=CATALOG, themes=THEMES)
				console = Console(file=io.StringIO(), width=100, color_system=None)
				store = SessionStore(Path(tmp) / "state")
				shell = Shell(console, None, None, Workspace(Path(tmp) / "42pal_exam"), rng=Random(42),
					sleep=lambda seconds: None, mode="revision", store=store, catalog=CATALOG, themes=THEMES)
				shell.retry = exam.retry["soft"]
				shell.start(exam, exam.playable_levels[0])
				played = []
				over = False
				while not over:
					self.assertLessEqual(len(played), exam.level_count, "more grademe than levels")
					played.append((shell.level, shell.variant.id))
					hand_in(shell)
					over = shell.handle("grademe")
					text = console.file.getvalue()
					# ✗ marks a failed grademe; the trace follows it.
					self.assertNotIn("✗", text, f"{exam_id}, level {played[-1]}:\n{text[-3000:]}")
				self.assertEqual([level for level, _ in played], list(range(1, exam.level_count + 1)))
				self.assertGreaterEqual(shell.grade, 100)
				self.assertEqual(store.history()[-1]["end"], "passed")
				self.assertIn("End of the exam", console.file.getvalue())
