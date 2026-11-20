"""Tests of pal42.report: what a tester pastes in an issue.

Run all the tests from the project root with: python3 -m unittest -v
"""

import getpass
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pal42 import __version__
from pal42.report import full_report, report, report_text
from pal42.session import Session, SessionStore

ROOT = Path(__file__).resolve().parent.parent

class TestReport(unittest.TestCase):
	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.store = SessionStore(Path(self.tmp.name) / "state")

	def tearDown(self):
		self.tmp.cleanup()

	def test_the_version_python_system_and_tools(self):
		lines = dict(report(ROOT, self.store))
		self.assertEqual(lines["version"], __version__)
		self.assertTrue(lines["python"].startswith(f"{sys.version_info.major}.{sys.version_info.minor}"))
		self.assertIn("Linux", lines["system"])
		self.assertIn("cc:", lines["tools"])
		self.assertIn("valgrind:", lines["tools"])

	def test_a_clone_says_its_commit_and_an_archive_says_so(self):
		lines = dict(report(ROOT, self.store))
		commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
			capture_output=True, text=True).stdout.strip()
		self.assertIn(commit, lines["install"])
		self.assertTrue(lines["install"].startswith("git clone"))
		self.assertEqual(dict(report(Path(self.tmp.name), self.store))["install"], "archive (no git)")

	def test_the_exam_in_progress_and_the_last_one(self):
		self.assertEqual(dict(report(ROOT, self.store))["exam"], "none in progress")
		self.store.save(Session(exam="rank02", level=2, variant="shift_letters#5", started_at=0, mode="revision",
			attempts=3, oks=1, failures=2, passed_levels=[1]))
		self.store.add_history({"exam": "rank03", "end": "passed", "grade": 100.00000000000001})
		lines = dict(report(ROOT, self.store))
		self.assertEqual(lines["exam"], "rank02, level 2, revision mode, subject shift_letters#5, 3 grademe")
		self.assertEqual(lines["last exam"], "rank03, passed, 100/100")

	def test_nothing_personal_in_it(self):
		"""No login, no home folder: it goes to a public issue."""
		text = report_text(ROOT, self.store)
		self.assertNotIn(getpass.getuser(), text)
		self.assertNotIn(str(Path.home()), text)
		self.assertTrue(text.startswith("42pal report"))

	def test_the_option_prints_it(self):
		result = subprocess.run([sys.executable, "-m", "pal42", "--report"], capture_output=True, text=True,
			cwd=ROOT)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn(f"version     {__version__}", result.stdout)

class TestFullReport(unittest.TestCase):
	"""full_report: the report of an issue about one subject, with the code and the last trace."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.store = SessionStore(Path(self.tmp.name) / "state")

	def tearDown(self):
		self.tmp.cleanup()

	def test_the_system_the_subject_the_code_and_the_trace(self):
		text = full_report("shift_letters#5 (forward_shift_3)", "Assignment name  : forward_shift_3\n",
			{"forward_shift_3.c": "int\tmain(void)\n{\n}\n", "other.h": None}, "= Test 1 ===\nDiff KO\n", "c",
			ROOT, self.store)
		self.assertTrue(text.startswith("# 42pal report\n"))
		self.assertIn(f"version     {__version__}", text)
		self.assertIn("## Subject: shift_letters#5 (forward_shift_3)", text)
		self.assertIn("```text\nAssignment name  : forward_shift_3\n```", text)
		self.assertIn("### forward_shift_3.c\n\n```c\nint\tmain(void)\n{\n}\n```", text)
		self.assertIn("### other.h\n\nmissing", text)
		self.assertIn("## Last trace\n\n```text\n= Test 1 ===\nDiff KO\n```", text)

	def test_no_trace_yet(self):
		text = full_report("x#1 (x)", "s", {"x.py": "pass\n"}, None, "python", ROOT, self.store)
		self.assertIn("```python\npass\n```", text)
		self.assertIn("## Last trace\n\nno grademe yet", text)
