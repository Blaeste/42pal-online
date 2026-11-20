"""Updates: is there a newer 42pal on the remote it was cloned from?

42pal is installed with git clone, so an update is a git pull. find_update
fetches the remote and tells whether the install can move forward to it;
apply_update pulls. Nothing here prints: the front-ends ask the question and
show the result. Like the rest of the core, this module only uses the
standard library.
"""

import os
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

# The folder of the install: the repository cloned by the student.
ROOT = Path(__file__).resolve().parent.parent

# Set to anything but empty, this variable turns the check off (the tests set it).
OFF_VARIABLE = "PAL42_NO_UPDATE"

# Seconds the fetch may take; with no network, the check gives up quietly.
FETCH_TIMEOUT = 8

# How many subjects of the new commits are shown.
CHANGES_SHOWN = 5

@dataclass(frozen=True)
class Update:
	"""A newer 42pal: how many new commits, and the subjects of the last ones."""
	count: int
	changes: tuple[str, ...]

def _git(root, *args, timeout=10):
	"""Run git in `root`; return its output, or None if it failed or took too long.

	git never asks a question here: no password prompt for an https remote,
	no passphrase for an ssh one. It fails instead, and the check gives up.
	"""
	env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
	env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
	try:
		result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
			timeout=timeout, env=env, stdin=subprocess.DEVNULL)
	except (OSError, subprocess.TimeoutExpired):
		return None
	return result.stdout if result.returncode == 0 else None

def find_update(root=ROOT, timeout=FETCH_TIMEOUT):
	"""Fetch the remote; return an Update if the install can go forward to it, else None.

	None too when the check is turned off, when root is not a git repository
	or follows no remote branch, when the fetch fails, and when the history
	has diverged (a pull could not simply go forward).
	"""
	if os.environ.get(OFF_VARIABLE) or not (Path(root) / ".git").exists():
		return None
	if _git(root, "rev-parse", "--abbrev-ref", "@{u}") is None:
		return None
	if _git(root, "fetch", "--quiet", timeout=timeout) is None:
		return None
	behind = _git(root, "rev-list", "--count", "HEAD..@{u}")
	if not behind or int(behind) == 0:
		return None
	# HEAD must be an ancestor of the remote branch: no commit of its own.
	if _git(root, "merge-base", "--is-ancestor", "HEAD", "@{u}") is None:
		return None
	subjects = _git(root, "log", "--format=%s", f"-n{CHANGES_SHOWN}", "HEAD..@{u}") or ""
	return Update(int(behind), tuple(subjects.splitlines()))

def apply_update(root=ROOT):
	"""Pull the new commits; return (True, "") or (False, why it failed).

	--ff-only: the pull only moves forward; it never merges, and git refuses
	it, changing nothing, if a file changed by hand would be overwritten.
	"""
	env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
	env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
	try:
		result = subprocess.run(["git", "-C", str(root), "pull", "--ff-only", "--quiet"],
			capture_output=True, text=True, timeout=60, env=env, stdin=subprocess.DEVNULL)
	except (OSError, subprocess.TimeoutExpired) as error:
		return False, str(error)
	if result.returncode != 0:
		return False, (result.stderr or result.stdout).strip()
	return True, ""

def restart():
	"""Start 42pal again, the new version, with the same arguments.

	It replaces the process: the code already loaded is the old one.
	"""
	os.execv(sys.executable, [sys.executable, "-m", "pal42", *sys.argv[1:]])

class UpdateCheck:
	"""find_update in a thread, started at launch: the student logs in meanwhile.

	finder is the function that looks (find_update by default; the tests
	give their own).
	"""

	def __init__(self, finder=find_update):
		self.finder = finder
		self.update = None
		self.thread = threading.Thread(target=self._run, daemon=True)

	def _run(self):
		self.update = self.finder()

	def start(self):
		self.thread.start()
		return self

	def result(self, wait=3):
		"""The Update found, or None: nothing new, or the check not done after `wait` s."""
		self.thread.join(wait)
		return None if self.thread.is_alive() else self.update
