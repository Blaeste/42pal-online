"""~/42pal_exam/: the folders the student works in, like at the exam.

subjects/<name>/subject.en.txt holds the subject, rendu/<name>/ is where
the student writes the code, and traces/ gets a trace for each failed
grademe. The student's work is never deleted.
"""

import getpass
import subprocess
from pathlib import Path

from pal42.subject import render

# Not ~/42pal: that is often where the repository itself was cloned.
DEFAULT_ROOT = Path.home() / "42pal_exam"

class Workspace:
	"""The exam folders, under `root` (~/42pal_exam by default).

	With a `remote` (a bare repository, like ~/.42pal/rendu.git), rendu/ is
	also a git repository that pushes to it: git add, commit and push work
	like at the exam, without being needed (grademe grades the files).
	"""

	def __init__(self, root=DEFAULT_ROOT, remote=None, git="git"):
		self.root = Path(root)
		self.remote = Path(remote) if remote else None
		self.git = git
		self.subjects = self.root / "subjects"
		self.rendu = self.root / "rendu"
		self.traces = self.root / "traces"
		# The reports written by the report command, to attach to an issue.
		self.reports = self.root / "reports"

	def give_subject(self, variant):
		"""Write the subject of `variant`, prepare its rendu folder, return the subject.

		exist_ok: folders already there are kept as they are, with the
		student's files in them.
		"""
		for folder in (self.subjects, self.rendu, self.traces):
			folder.mkdir(parents=True, exist_ok=True)
		subject = self.subjects / variant.name / "subject.en.txt"
		subject.parent.mkdir(exist_ok=True)
		subject.write_text(render(variant), encoding="utf-8")
		# Files given by the exercise (a header with a struct...), for the student.
		for name, content in variant.provided_files.items():
			(subject.parent / name).write_text(content, encoding="utf-8")
		(self.rendu / variant.name).mkdir(exist_ok=True)
		if self.remote:
			self._ensure_git()
		return subject

	def _ensure_git(self):
		"""Make rendu/ a git repository pushing to `remote`, the first time only.

		Without git (or if git fails), rendu/ simply stays a plain folder.
		"""
		if (self.rendu / ".git").exists():
			return

		def run(*args, cwd):
			return subprocess.run(
				[self.git, *args], cwd=cwd, capture_output=True, text=True, check=True,
			)

		try:
			self.remote.parent.mkdir(parents=True, exist_ok=True)
			if not self.remote.exists():
				run("init", "--bare", "-b", "main", str(self.remote), cwd=self.remote.parent)
			run("init", "-b", "main", cwd=self.rendu)
			run("remote", "add", "origin", str(self.remote), cwd=self.rendu)
			# A plain `git push` then works at once, with no upstream to set.
			run("config", "push.default", "current", cwd=self.rendu)
			# No identity at all: git commit would refuse; give a local one.
			if subprocess.run([self.git, "config", "user.email"], cwd=self.rendu,
					capture_output=True).returncode != 0:
				run("config", "user.name", getpass.getuser(), cwd=self.rendu)
				run("config", "user.email", f"{getpass.getuser()}@42pal.local", cwd=self.rendu)
		except (OSError, subprocess.CalledProcessError):
			return

	def write_trace(self, attempt, name, text):
		"""Write the log of grademe number `attempt` in traces/ and return its path.

		Named like 01_<name>.trace, so that the logs sort in order.
		"""
		self.traces.mkdir(parents=True, exist_ok=True)
		log = self.traces / f"{attempt:02d}_{name}.trace"
		log.write_text(text, encoding="utf-8")
		return log
