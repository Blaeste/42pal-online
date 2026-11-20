"""Tests of pal42.session: the exam in progress and the history, in ~/.42pal/.

Run all the tests from the project root with: python3 -m unittest -v
"""

import tempfile
import unittest
from pathlib import Path

from pal42.session import Session, SessionStore

SESSION = Session(
	exam="rank02", level=2, variant="char_filter#17", started_at=1_700_000_000.0,
	mode="exam", attempts=3, oks=1, failures=2, passed_levels=[1],
	next_grademe_at=1_700_000_600.0, warned=False,
)

class TestSessionStore(unittest.TestCase):
	"""SessionStore(folder): session.json and history.json in that folder."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.store = SessionStore(Path(self.tmp.name) / ".42pal")

	def tearDown(self):
		self.tmp.cleanup()

	def test_saving_then_loading_gives_the_same_session(self):
		"""Every field comes back as it was, even in a new store."""
		self.store.save(SESSION)
		self.assertEqual(SessionStore(self.store.folder).load(), SESSION)

	def test_no_session_and_a_broken_file_both_give_none(self):
		"""Nothing saved, or a file that is not a session: no session, no crash."""
		self.assertIsNone(self.store.load())
		self.store.folder.mkdir(parents=True)
		(self.store.folder / "session.json").write_text("{not json", encoding="utf-8")
		self.assertIsNone(self.store.load())

	def test_clear_removes_the_session(self):
		"""Once the exam is over, there is nothing to resume."""
		self.store.save(SESSION)
		self.store.clear()
		self.assertIsNone(self.store.load())

	def test_finished_exams_are_kept_in_the_history_across_sessions(self):
		"""Each finished exam is added; a new store finds them all, in order."""
		first = {"exam": "rank02", "levels_passed": [1], "attempts": 2, "oks": 1}
		second = {"exam": "piscine", "levels_passed": [], "attempts": 1, "oks": 0}
		self.store.add_history(first)
		SessionStore(self.store.folder).add_history(second)
		self.assertEqual(SessionStore(self.store.folder).history(), [first, second])

	def test_broken_history_gives_an_empty_one(self):
		"""history.json cut in the middle: an empty history, no crash."""
		self.store.folder.mkdir(parents=True)
		(self.store.folder / "history.json").write_text("[{", encoding="utf-8")
		self.assertEqual(self.store.history(), [])
