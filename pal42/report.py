"""./42pal --report: what a tester pastes in an issue when something goes wrong.

The version of 42pal and how it was installed, the versions of Python and
of the tools, the system, the terminal, and the exam in progress. Nothing
personal: no login, no path to a home folder, no code of the student. Like
the rest of the core, this module never prints: --report prints the text.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from pal42 import __version__
from pal42.session import SessionStore
from pal42.update import ROOT

def _first_line(*command):
	"""The first line that `command` prints, or "missing" if it is not on the machine."""
	try:
		done = subprocess.run(command, capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL)
	except (OSError, subprocess.TimeoutExpired):
		return "missing"
	output = (done.stdout or done.stderr).strip()
	return output.splitlines()[0] if output else "missing"

def _install(root):
	"""How 42pal was installed: a git clone and its commit, or an archive."""
	if not (Path(root) / ".git").exists():
		return "archive (no git)"
	git = ["git", "-C", str(root)]
	try:
		commit = subprocess.run([*git, "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
			timeout=5).stdout.strip()
		branch = subprocess.run([*git, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True,
			timeout=5).stdout.strip()
		changed = subprocess.run([*git, "status", "--porcelain", "--untracked-files=no"], capture_output=True,
			text=True, timeout=5).stdout.strip()
	except (OSError, subprocess.TimeoutExpired):
		return "git clone (git missing)"
	return f"git clone, {branch} at {commit}" + (" with local changes" if changed else "")

def _system():
	"""The system, its kernel and its distribution, as the machine names them."""
	name = ""
	try:
		for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
			if line.startswith("PRETTY_NAME="):
				name = ", " + line.split("=", 1)[1].strip('"')
	except OSError:
		pass
	return f"{platform.system()} {platform.release()} {platform.machine()}{name}"

def _grade(value):
	return f"{round(value, 2):g}"

def report(root=ROOT, store=None):
	"""The lines of the report: (label, value) pairs, in order."""
	store = store or SessionStore()
	size = shutil.get_terminal_size()
	tools = " · ".join(f"{tool}: {_first_line(tool, '--version')}" for tool in ("cc", "valgrind", "git"))
	lines = [
		("version", __version__),
		("install", _install(root)),
		("python", platform.python_version()),
		("system", _system()),
		("terminal", f"{os.environ.get('TERM', 'unknown')}, {size.columns}x{size.lines}"
			+ (", stdin not a terminal" if not sys.stdin.isatty() else "")),
		("tools", tools),
	]
	session = store.load()
	if session is None:
		lines.append(("exam", "none in progress"))
	else:
		lines.append(("exam", f"{session.exam}, level {session.level}, {session.mode} mode, "
			f"subject {session.variant}, {session.attempts} grademe"))
	history = store.history()
	if history:
		last = history[-1]
		lines.append(("last exam", f"{last.get('exam')}, {last.get('end')}, {_grade(last.get('grade', 0))}/100"))
	return lines

def report_text(root=ROOT, store=None):
	"""The report as text, ready to paste: a title, then a line per item."""
	lines = report(root, store)
	return "42pal report (paste it in your issue)\n" + "".join(
		f"{label:12}{value}\n" for label, value in lines)

def full_report(subject_id, subject, files, trace, language, root=ROOT, store=None):
	"""The report of an issue about one subject, in Markdown, ready to attach or paste.

	The report above, then the subject, the student's files ({name: text, or
	None when the file is missing}) and the last trace (None before the first
	grademe). language names the code blocks ("c", "python"). Unlike the
	report above, it holds the student's code: the student shares it or not.
	"""
	system = report_text(root, store).split("\n", 1)[1].rstrip("\n")
	parts = ["# 42pal report", "", "## System", "", "```text", system, "```", "",
		f"## Subject: {subject_id}", "", "```text", subject.rstrip("\n"), "```", "", "## Code", ""]
	for name, text in files.items():
		parts += [f"### {name}", ""]
		parts += ["missing", ""] if text is None else [f"```{language}", text.rstrip("\n"), "```", ""]
	parts += ["## Last trace", ""]
	parts += ["no grademe yet"] if trace is None else ["```text", trace.rstrip("\n"), "```"]
	return "\n".join(parts) + "\n"
