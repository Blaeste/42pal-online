"""Tests of tools/ci_scope.py: what the tests of GitHub check, from the files changed.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

SCOPE = run_path(str(Path(__file__).resolve().parent.parent / "tools" / "ci_scope.py"))["scope"]

class TestScope(unittest.TestCase):
	def test_docs_only_check_nothing(self):
		self.assertEqual(SCOPE(["README.md", "docs/plans/42pal.md", "LICENSE", ".github/ISSUE_TEMPLATE/bug.yml"]),
			"none")

	def test_exercises_only_check_those_exercises(self):
		self.assertEqual(SCOPE(["exercises/c/word_each/ref.c", "exercises/python/key_sort/exercise.py",
			"exercises/c/word_each/exercise.py", "tests/test_rank02_more.py"]), "key_sort word_each")

	def test_the_core_or_the_catalog_files_check_everything(self):
		for changed in ("pal42/grader.py", "themes.json", "exams/rank02.json", "42pal", ".github/workflows/tests.yml",
				"tests/helpers.py", "tests/test_reference.py", "vendor/rich/text.py", "tools/ci_scope.py"):
			with self.subTest(changed):
				self.assertEqual(SCOPE(["exercises/c/word_each/ref.c", changed]), "all")

	def test_the_interface_changes_no_grading(self):
		"""The screens, the report, the progress...: their own tests run, not every exercise again."""
		self.assertEqual(SCOPE(["pal42/cli/tui.py", "pal42/cli/tui.tcss", "pal42/report.py", "pal42/progress.py",
			"pal42/session.py", "pal42/update.py", "pal42/cheat.py", "pal42/cheat.pack"]), "none")
		self.assertEqual(SCOPE(["pal42/cli/check.py"]), "all")
		self.assertEqual(SCOPE(["pal42/cli/display.py", "exercises/c/word_each/ref.c"]), "word_each")

	def test_other_tests_change_nothing_to_check(self):
		self.assertEqual(SCOPE(["tests/test_cli.py"]), "none")
