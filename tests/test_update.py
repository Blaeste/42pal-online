"""Tests of pal42.update: a newer 42pal on the remote it was cloned from.

Each test builds real git repositories in a temporary folder: a bare remote,
the install (a clone of it), and another clone that pushes new commits.

Run all the tests from the project root with: python3 -m unittest -v
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pal42.update import Update, UpdateCheck, apply_update, find_update

def git(*args, cwd):
	subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
		env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
			GIT_COMMITTER_EMAIL="t@t"))

def commit(folder, name, message):
	(folder / name).write_text(message, encoding="utf-8")
	git("add", name, cwd=folder)
	git("commit", "-q", "-m", message, cwd=folder)

@unittest.skipUnless(shutil.which("git"), "git is not installed")
class TestUpdate(unittest.TestCase):
	"""find_update and apply_update on real repositories."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		root = Path(self.tmp.name)
		self.remote = root / "remote.git"
		git("init", "-q", "--bare", "-b", "main", str(self.remote), cwd=root)
		self.other = root / "other"
		git("clone", "-q", str(self.remote), str(self.other), cwd=root)
		git("checkout", "-q", "-b", "main", cwd=self.other)
		commit(self.other, "a.txt", "first")
		git("push", "-q", "-u", "origin", "main", cwd=self.other)
		self.install = root / "install"
		git("clone", "-q", str(self.remote), str(self.install), cwd=root)
		# The variable the tests of the other modules set must not stop these.
		self.env = mock.patch.dict(os.environ, {"PAL42_NO_UPDATE": ""})
		self.env.start()

	def tearDown(self):
		self.env.stop()
		self.tmp.cleanup()

	def test_nothing_new_gives_none(self):
		self.assertIsNone(find_update(self.install))

	def test_new_commits_are_found_with_their_subjects(self):
		"""Two commits pushed: count 2, the newest subject first."""
		commit(self.other, "b.txt", "feat: add b")
		commit(self.other, "c.txt", "fix: repair c")
		git("push", "-q", cwd=self.other)
		self.assertEqual(find_update(self.install), Update(2, ("fix: repair c", "feat: add b")))

	def test_apply_update_pulls_the_new_commits(self):
		commit(self.other, "b.txt", "feat: add b")
		git("push", "-q", cwd=self.other)
		ok, why = apply_update(self.install)
		self.assertTrue(ok, why)
		self.assertTrue((self.install / "b.txt").is_file())
		self.assertIsNone(find_update(self.install))

	def test_diverged_history_is_not_offered(self):
		"""A local commit the remote does not have: a pull could not go forward."""
		commit(self.other, "b.txt", "feat: add b")
		git("push", "-q", cwd=self.other)
		commit(self.install, "local.txt", "my own change")
		self.assertIsNone(find_update(self.install))

	def test_a_failed_pull_says_why_and_changes_nothing(self):
		"""A file changed by hand that the pull would overwrite."""
		commit(self.other, "a.txt", "second")
		git("push", "-q", cwd=self.other)
		(self.install / "a.txt").write_text("edited by hand", encoding="utf-8")
		ok, why = apply_update(self.install)
		self.assertFalse(ok)
		self.assertTrue(why)
		self.assertEqual((self.install / "a.txt").read_text(encoding="utf-8"), "edited by hand")

	def test_no_git_no_remote_or_turned_off_gives_none(self):
		"""A folder that is no repository, a repository with no upstream, PAL42_NO_UPDATE."""
		self.assertIsNone(find_update(Path(self.tmp.name)))
		alone = Path(self.tmp.name) / "alone"
		git("init", "-q", str(alone), cwd=self.tmp.name)
		self.assertIsNone(find_update(alone))
		commit(self.other, "b.txt", "feat: add b")
		git("push", "-q", cwd=self.other)
		with mock.patch.dict(os.environ, {"PAL42_NO_UPDATE": "1"}):
			self.assertIsNone(find_update(self.install))

class TestUpdateCheck(unittest.TestCase):
	"""The check runs in a thread, while the student logs in."""

	def test_the_result_once_the_thread_is_done(self):
		check = UpdateCheck(lambda: Update(1, ("feat: x",)))
		check.start()
		self.assertEqual(check.result(wait=5), Update(1, ("feat: x",)))

	def test_a_check_that_takes_too_long_gives_none(self):
		import threading
		release = threading.Event()
		check = UpdateCheck(lambda: release.wait(5) and Update(1, ()))
		check.start()
		self.assertIsNone(check.result(wait=0.05))
		release.set()
