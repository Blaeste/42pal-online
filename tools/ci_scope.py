"""Which exercises the tests of GitHub go through: only what changed, and what it can break.

	python3 tools/ci_scope.py BASE HEAD

prints "all", "none", or the names of the exercises changed between the
two commits. The workflow gives it to the tests in PAL42_EXERCISES: the
tests that go through every exercise (compiling each ref.c, check-catalog)
then only go through those. The other tests always run.

- the docs (README, docs/, LICENSE, the issue templates) change nothing to
  check: "none" (the workflow is not even started for them alone);
- files of exercises: those exercises only;
- the other tests, and the interface (pal42/cli/ but check.py, the report,
  the progress, the session, the updates, the cheat menu): nothing more to
  check, they grade no exercise (their own tests run anyway);
- anything else (pal42/, themes.json, exams/, the launcher, vendor/, the
  workflow, the helpers of the tests...) can change every exercise: "all".

With no base commit (a new branch), or when git cannot tell: "all".
"""

import subprocess
import sys

# Changes that nothing has to be checked for.
IGNORED = ("README.md", "LICENSE", ".gitignore", ".gitattributes")
IGNORED_FOLDERS = ("docs/", ".github/ISSUE_TEMPLATE/")

# The interface: it grades no exercise. pal42/cli/check.py is check-catalog itself.
INTERFACE = ("pal42/cli/", "pal42/report.py", "pal42/progress.py", "pal42/session.py", "pal42/update.py",
	"pal42/cheat.py", "pal42/cheat.pack")

# Tests that every exercise goes through, and what all the tests share.
TESTS_FOR_ALL = ("tests/__init__.py", "tests/helpers.py", "tests/test_reference.py", "tests/test_smoke.py")

def scope(files):
	"""From the changed files: "all", "none", or the names of the changed exercises."""
	names = set()
	for file in files:
		if file in IGNORED or file.startswith(IGNORED_FOLDERS):
			continue
		if file.startswith("tests/") and file not in TESTS_FOR_ALL:
			continue
		if file.startswith(INTERFACE) and file != "pal42/cli/check.py":
			continue
		parts = file.split("/")
		# exercises/<language>/<name>/<file>
		if parts[0] == "exercises" and len(parts) >= 4:
			names.add(parts[2])
			continue
		return "all"
	return " ".join(sorted(names)) or "none"

def main(args):
	base, head = (args + ["", ""])[:2]
	if not base or set(base) == {"0"}:
		print("all")
		return 0
	try:
		done = subprocess.run(["git", "diff", "--name-only", base, head or "HEAD"], capture_output=True,
			text=True, timeout=30)
	except (OSError, subprocess.TimeoutExpired):
		print("all")
		return 0
	print("all" if done.returncode else scope(done.stdout.split()))
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
