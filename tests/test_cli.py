"""Tests of pal42.cli: the terminal front-end (display, workspace, shell).

Run all the tests from the project root with: python3 -m unittest -v
"""

import getpass
import os
import pty
import re
import select
import signal
import shutil
import subprocess
import time
import io
import tempfile
import threading
import unittest
from unittest import mock
from pathlib import Path
from random import Random

from pal42.cli.practice import PracticeShell
from pal42.cli.shell import Shell, complete_command
from pal42.catalog import Catalog, load_catalog
from pal42.cli import check, display
from pal42.cli.workspace import Workspace
from pal42.exam import load_exam
from pal42.grader import Grade
from pal42.retry import RetryPolicy
from pal42.session import Session, SessionStore
from pal42.subject import render
from pal42.themes import Theme, load_themes
from pal42.update import Update
from pal42.variant import Variant
from rich.console import Console
from tests.helpers import ECHO, ECHO_OK, echo_oracle, echo_tests, make_exercise

ROOT = Path(__file__).resolve().parent.parent

# Made-up themes and catalog: one exercise, playable at rank02 levels 2 and 3.
THEMES = {"char_sets": Theme("char_sets", "Compare characters", {"rank02": (2, 3)})}
CATALOG = Catalog({"char_filter": make_exercise()}, [])
# echo_first, an exercise that can really be graded, at rank02 levels 1 and 2.
ECHO_THEMES = {"char_sets": Theme("char_sets", "Compare characters", {"rank02": (1, 2)})}
ECHO_CATALOG = Catalog({"echo_first": ECHO.exercise}, [])

class TestVendoredRich(unittest.TestCase):
	"""rich comes from vendor/: nothing to install, no sudo."""

	def test_cli_uses_the_rich_copied_in_vendor(self):
		"""Importing pal42.cli makes the rich of vendor/ importable first."""
		import pal42.cli  # noqa: F401  (imported for its effect on sys.path)
		import rich
		self.assertEqual(Path(rich.__file__).resolve().parent, ROOT / "vendor" / "rich")

class TestWorkspace(unittest.TestCase):
	"""~/42pal_exam/: subjects/, rendu/ and traces/, like at the exam."""

	def setUp(self):
		"""A temporary folder stands for ~/42pal_exam in each test."""
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.variant = Variant(load_catalog().exercises["char_filter"], 0,
			{"mode": "common", "order": "ascii", "separator": "space"})

	def tearDown(self):
		self.tmp.cleanup()

	def test_give_subject_writes_it_and_prepares_the_rendu_folder(self):
		"""subjects/<name>/subject.en.txt holds the subject; rendu/<name>/ waits."""
		workspace = Workspace(self.root)
		path = workspace.give_subject(self.variant)
		self.assertEqual(path, self.root / "subjects/common_chars/subject.en.txt")
		self.assertEqual(path.read_text(encoding="utf-8"), render(self.variant))
		self.assertTrue((self.root / "rendu/common_chars").is_dir())
		self.assertTrue((self.root / "traces").is_dir())

	def test_given_files_are_written_next_to_the_subject(self):
		"""A header given by the exercise lands in subjects/<name>/."""
		variant = Variant(make_exercise(provided_files={"point.h": "typedef int\tt_x;\n"}),
			0, {"mode": "common"})
		Workspace(self.root).give_subject(variant)
		given = self.root / "subjects/char_filter/point.h"
		self.assertEqual(given.read_text(encoding="utf-8"), "typedef int\tt_x;\n")

	def test_student_work_already_in_rendu_is_kept(self):
		"""Giving a subject again never deletes what the student wrote."""
		work = self.root / "rendu/common_chars/common_chars.c"
		work.parent.mkdir(parents=True)
		work.write_text("int main(void) { return 0; }\n", encoding="utf-8")
		Workspace(self.root).give_subject(self.variant)
		self.assertEqual(work.read_text(encoding="utf-8"), "int main(void) { return 0; }\n")

class Script:
	"""Answers given in order, as if a student typed them.

	An empty answer takes the default, like pressing Enter. When there is no
	answer left, EOFError is raised, like Ctrl-D.
	"""

	def __init__(self, *answers):
		self.answers = list(answers)
		self.prompts = []

	def ask(self, prompt, default=None):
		self.prompts.append(prompt)
		if not self.answers:
			raise EOFError
		answer = self.answers.pop(0)
		# A function stands for something done before typing (like letting
		# time pass): it is called, and what it returns is the answer.
		if callable(answer):
			answer = answer()
		return default if answer == "" and default is not None else answer

	def ask_password(self, prompt):
		self.prompts.append(prompt)
		return self.answers.pop(0)

class FakeClock:
	"""A clock that only moves when the test says so, in seconds."""

	def __init__(self):
		self.now = 1000.0

	def __call__(self):
		return self.now

def make_shell(script, root, clock=None):
	"""A shell that reads `script` and writes into a string, not the screen."""
	console = Console(file=io.StringIO(), width=100, color_system=None)
	return Shell(console, script.ask, script.ask_password, Workspace(root),
		rng=Random(1), clock=clock or FakeClock(), sleep=lambda seconds: None)

def output(shell):
	"""Everything the shell has printed."""
	return shell.console.file.getvalue()

class TestReportCommand(unittest.TestCase):
	"""report in the examshell: a file with the system, the subject, the code and the last trace."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"

	def tearDown(self):
		self.tmp.cleanup()

	def test_report_writes_a_file_to_attach_to_an_issue(self):
		shell = make_shell(Script(), self.root)
		shell.start(load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES), 2)
		rendu = self.root / "rendu" / shell.variant.name
		rendu.mkdir(parents=True, exist_ok=True)
		(rendu / "echo_first.c").write_text("int\tmain(void)\n{\n\treturn (1);\n}\n", encoding="utf-8")
		shell.handle("grademe")
		shell.handle("report")
		reports = list((self.root / "reports").glob("*_echo_first.md"))
		self.assertEqual(len(reports), 1)
		text = reports[0].read_text(encoding="utf-8")
		self.assertIn(f"## Subject: {shell.variant.id} (echo_first)", text)
		self.assertIn("return (1);", text)
		self.assertIn("Diff KO", text)
		self.assertIn("Report written", output(shell))
		self.assertEqual(shell.last_report, reports[0])

	def test_report_is_in_the_help(self):
		shell = make_shell(Script(), self.root)
		shell.start(load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES), 2)
		shell.handle("help")
		self.assertIn("report", output(shell))

class TestHelpTable(unittest.TestCase):
	def test_the_help_says_how_to_report_a_problem(self):
		console = Console(file=io.StringIO(), width=100, color_system=None)
		console.print(display.help_table({"grademe": "grade your work"}))
		self.assertIn("./42pal --report", console.file.getvalue())

class TestPoints(unittest.TestCase):
	"""display.points: the points of a level and the grade, as a student reads them."""

	def test_two_decimals_at_most_and_no_useless_zero(self):
		"""6 levels make 16.67 points each, not 16.6667; 25 stays 25, 12.5 stays 12.5."""
		self.assertEqual(display.points(100 / 6), "16.67")
		self.assertEqual(display.points(100 / 3), "33.33")
		self.assertEqual(display.points(100 / 6 * 6), "100")
		self.assertEqual(display.points(25.0), "25")
		self.assertEqual(display.points(12.5), "12.5")
		self.assertEqual(display.points(0), "0")

class TestShell(unittest.TestCase):
	"""The examshell, driven by a Script."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"

	def tearDown(self):
		self.tmp.cleanup()

	def test_fake_login_takes_any_password_and_keeps_none(self):
		"""The login defaults to the user name; the password is never kept."""
		script = Script("", "my-secret-password")
		shell = make_shell(script, self.root)
		shell.login()
		self.assertEqual(shell.user, getpass.getuser())
		self.assertIn(f"Welcome {getpass.getuser()}!\n\n", output(shell))
		self.assertNotIn("my-secret-password", output(shell))
		self.assertNotIn("my-secret-password", repr(vars(shell)))

	def test_the_first_menu_asks_piscine_or_student(self):
		"""5 and x are refused; 1 is the piscine, 2 the students, 3 practice; 4 quits."""
		shell = make_shell(Script("5", "x", "1"), self.root)
		self.assertEqual(shell.choose_audience(), "piscine")
		text = output(shell)
		self.assertIn("1. Piscine (piscineux)", text)
		self.assertIn("2. Student (cursus)", text)
		self.assertIn("3. Practice", text)
		self.assertIn("4. Quit", text)
		self.assertEqual(text.count("Invalid choice"), 2)
		self.assertEqual(make_shell(Script("2"), self.root).choose_audience(), "student")

	def test_exam_menu_shows_the_exams_of_the_audience_with_levels_and_time(self):
		"""Piscine: its 4 exams only, each with its levels and duration; 9 is refused."""
		shell = make_shell(Script("9", "2"), self.root)
		exam = shell.choose_exam("piscine")
		self.assertEqual(exam.id, "piscine_02")
		text = output(shell)
		self.assertRegex(text, r"1\. Piscine Exam 01 +8 levels, 4 h, C")
		self.assertRegex(text, r"4\. Piscine Final Exam +4 levels, 8 h, C")
		self.assertIn("5. Back (previous menu)", text)
		self.assertNotIn("Rank 02", text)
		self.assertEqual(text.count("Invalid choice"), 1)

	def test_a_student_goes_from_the_first_menu_to_the_mode(self):
		"""2 (student): the menu of the rank 02 and the rank 03, then the mode and the level."""
		script = Script("", "pw", "2", "1", "", "", "finish")
		shell = make_shell(script, self.root)
		shell.run()
		self.assertEqual(shell.exam.id, "rank02")
		self.assertEqual(script.prompts[2:6], ["Your choice:", "Exam:", "Mode:", "Starting level:"])
		self.assertRegex(output(shell), r"2\. Exam Rank 03 +6 levels, 3 h, Python")

	def test_exam_mode_starts_at_level_1_without_asking(self):
		"""Like the real exam: no starting level to choose in exam mode."""
		script = Script("", "pw", "2", "1", "1", "finish")
		shell = make_shell(script, self.root)
		shell.run()
		self.assertEqual((shell.mode, shell.level), ("exam", 1))
		self.assertNotIn("Starting level:", script.prompts)
		self.assertIn("Exam mode starts at level 1, like the real exam.", output(shell))

	def test_back_goes_to_the_menu_before_and_skips_the_menus_not_shown(self):
		"""Back from the piscine exams, back from the student exams, then a piscine exam."""
		# Back is the last choice: after the exams of the students (the ranks).
		ranks = [exam for exam in make_shell(Script(), self.root)._exams() if exam.audience == "student"]
		answers = ("", "pw", "1", "5", "2", str(len(ranks) + 1), "1", "2", "", "", "finish")
		shell = make_shell(Script(*answers), self.root)
		shell.run()
		self.assertEqual((shell.exam.id, shell.mode, shell.level), ("piscine_02", "revision", 1))
		self.assertEqual(output(shell).count("What do you want to do?"), 3)

	def test_practice_is_a_choice_of_the_first_menu(self):
		"""Practice, Python, its first theme: a practice subject, then finish."""
		script = Script("", "pw", "3", "2", "1", "finish")
		shell = make_shell(script, self.root)
		shell.run()
		text = output(shell)
		self.assertIn("What do you want to do?", text)
		self.assertRegex(text, r"3\. Practice +one theme, no timer")
		self.assertIn("Choose a language:", text)
		self.assertIn("Practice summary", text)
		self.assertIn("practice>", script.prompts)
		self.assertNotIn("examshell>", script.prompts)

	def test_back_from_the_practice_menus_goes_to_the_first_menu(self):
		"""Back from the languages: the first menu again, then quit."""
		script = Script("", "pw", "3", "3", "4")
		shell = make_shell(script, self.root)
		shell.run()
		text = output(shell)
		self.assertEqual(text.count("What do you want to do?"), 2)
		self.assertIn("3. Back (previous menu)", text)
		self.assertIn("Goodbye!", text)

	def test_back_from_the_level_menu_goes_to_the_mode_menu(self):
		"""Revision, back from the levels, then exam mode: level 1, no level menu."""
		shell = make_shell(Script("", "pw", "2", "1", "2", "5", "1", "finish"), self.root)
		shell.run()
		self.assertEqual((shell.mode, shell.level), ("exam", 1))
		self.assertEqual(output(shell).count("Choose the mode:"), 2)

	def test_quit_in_the_first_menu_starts_no_exam(self):
		"""4 in the first menu: goodbye, no subject, no examshell."""
		script = Script("", "pw", "4")
		shell = make_shell(script, self.root)
		shell.run()
		self.assertIsNone(shell.exam)
		self.assertIn("Goodbye!", output(shell))
		self.assertNotIn("examshell>", script.prompts)

	def test_the_first_menu_shown_quits_even_when_it_is_the_mode(self):
		"""One exam only: the mode menu comes first, and its last choice is Quit."""
		console = Console(file=io.StringIO(), width=100, color_system=None)
		script = Script("", "pw", "3")
		shell = Shell(console, script.ask, script.ask_password, Workspace(self.root),
			rng=Random(1), clock=FakeClock(), sleep=lambda seconds: None,
			catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		shell.run()
		self.assertIn("3. Quit", output(shell))
		self.assertIsNone(shell.exam)

	def test_a_single_exam_is_taken_without_asking(self):
		"""With C exercises only, the students have the rank 02 only: no question, it is said."""
		shell = make_shell(Script(), self.root)
		c_only = load_catalog()
		c_only.exercises = {name: exo for name, exo in c_only.exercises.items() if exo.language == "c"}
		shell._catalog = lambda: (c_only, load_themes())
		self.assertEqual(shell.choose_exam("student").id, "rank02")
		self.assertIn("Your exam: Exam Rank 02 (4 levels, 3 h, C)", output(shell))

	def test_level_menu_says_what_a_level_is_worth(self):
		"""25 points a level; the levels skipped give none; level 1 is not playable here."""
		shell = make_shell(Script("1", ""), self.root)
		level = shell.choose_level(load_exam("rank02", catalog=CATALOG, themes=THEMES))
		self.assertEqual(level, 2)
		text = " ".join(output(shell).split())
		self.assertIn("4 levels, worth 25 points each: pass them all for 100/100.", text)
		self.assertIn("If you start higher, the levels before it give no points.", text)
		self.assertIn("Levels you can play: 2, 3", text)
		self.assertIn("5. Back (previous menu)", text)
		self.assertEqual(text.count("Invalid choice"), 1)

	def test_mode_menu_explains_exam_and_revision(self):
		"""Exam: the real duration and the hard waits; revision: no limit, soft waits."""
		exam = load_exam("rank02", catalog=CATALOG, themes=THEMES)
		shell = make_shell(Script("x", ""), self.root)
		self.assertEqual(shell.choose_mode(exam), "revision")
		text = " ".join(output(shell).split())
		self.assertIn("1. Exam The real conditions: 3 h, then the exam ends. Waits after a "
			"failed grademe grow fast (minutes): 0.5, 2.5, 3, 5.5, 8.5, 14, 22.5, 36.5, 59", text)
		self.assertIn("2. Revision No time limit. Waits after a failed grademe stay short "
			"(minutes): 0, 1, 2, 3, 5", text)
		self.assertIn("3. Back (previous menu)", text)
		self.assertIn("Enter alone takes revision.", text)
		self.assertEqual(text.count("Invalid choice"), 1)
		self.assertEqual(make_shell(Script("1"), self.root).choose_mode(exam), "exam")

	def test_the_mode_sets_the_waits_and_is_shown(self):
		"""Revision by default: soft waits, shown in the panel and in status."""
		shell = make_shell(Script("", "pw", "2", "1", "", "", "status", "finish"), self.root)
		shell.run()
		self.assertEqual((shell.mode, shell.retry), ("revision", shell.exam.retry["soft"]))
		self.assertIn("revision mode", output(shell))
		self.assertRegex(output(shell), r"Time left\s+no limit")
		exam_shell = make_shell(Script("", "pw", "2", "1", "1", "finish"), self.root)
		exam_shell.run()
		self.assertEqual(exam_shell.retry, exam_shell.exam.retry["hard"])
		self.assertIn("exam mode", output(exam_shell))

	def test_start_gives_the_subject_and_says_where_it_is(self):
		"""A subject is drawn at the level, written, and its paths are shown."""
		shell = make_shell(Script(), self.root)
		shell.start(load_exam("rank02", catalog=CATALOG, themes=THEMES), 2)
		name = shell.variant.name
		self.assertTrue((self.root / "subjects" / name / "subject.en.txt").exists())
		self.assertTrue((self.root / "rendu" / name).is_dir())
		self.assertIn(name, output(shell))
		self.assertIn(f"subjects/{name}/subject.en.txt", output(shell))
		self.assertIn(f"rendu/{name}/", output(shell))

	def test_panel_comes_before_the_subject_and_is_as_wide(self):
		"""First the panel (where to read and hand in), 80 wide like the subject."""
		shell = make_shell(Script(), self.root)
		shell.start(load_exam("rank02", catalog=CATALOG, themes=THEMES), 2)
		text = output(shell)
		self.assertLess(text.index("Read it"), text.index("Assignment name"))
		top_border = next(line for line in text.splitlines() if line.startswith("╭"))
		self.assertEqual(len(top_border), 80)

	def test_start_also_prints_the_whole_subject(self):
		"""The subject is in subject.en.txt and also printed, as plain text."""
		shell = make_shell(Script(), self.root)
		shell.start(load_exam("rank02", catalog=CATALOG, themes=THEMES), 2)
		self.assertIn(render(shell.variant), output(shell))

	def test_commands_help_status_grademe_and_unknown(self):
		"""Each command answers; status shows the time spent and the time left."""
		clock = FakeClock()
		shell = make_shell(Script("help", "status", "grademe", "foo", "finish"), self.root, clock)
		shell.start(load_exam("rank02", catalog=CATALOG, themes=THEMES), 2)
		clock.now += 600
		shell.command_loop()
		text = output(shell)
		for command in ["status", "grademe", "finish", "help"]:
			self.assertIn(command, text)
		self.assertIn("0:10:00", text)
		self.assertIn("2:50:00", text)
		self.assertIn("Missing file", text)
		self.assertIn("Unknown command: foo", text)
		self.assertIn("End of the exam", text)

	def test_a_blank_line_separates_each_answer_from_the_next_prompt(self):
		"""After each command's answer, a blank line; Enter alone adds nothing."""
		shell = make_shell(Script("foo", "", "bar", "finish"), self.root)
		shell.start(load_exam("rank02", catalog=CATALOG, themes=THEMES), 2)
		shell.command_loop()
		text = output(shell)
		self.assertIn("Type help for the list.\n\nUnknown command: bar", text)
		# Both answers are followed by a blank line; Enter alone added none.
		self.assertEqual(text.count("Type help for the list.\n\n"), 2)
		self.assertNotIn("\n\n\n", text.split("Display the characters")[1])

	def test_ctrl_d_ends_the_exam_cleanly(self):
		"""No answer left (Ctrl-D): the exam ends, nothing crashes."""
		shell = make_shell(Script(), self.root)
		shell.start(load_exam("rank02", catalog=CATALOG, themes=THEMES), 2)
		shell.command_loop()
		self.assertIn("End of the exam", output(shell))

	def test_run_goes_from_login_to_finish(self):
		"""Login, student, the rank 02, the first playable level, status, then finish."""
		shell = make_shell(Script("", "pw", "2", "1", "", "", "status", "finish"), self.root)
		shell.run()
		text = output(shell)
		self.assertIn("Welcome", text)
		self.assertIn("Exam Rank 02", text)
		self.assertIn("Time left", text)
		self.assertIn("End of the exam", text)
		self.assertEqual(len(list(self.root.glob("subjects/*/subject.en.txt"))), 1)

class TestLauncher(unittest.TestCase):
	"""./42pal with no argument starts the examshell."""

	def test_42pal_starts_the_examshell(self):
		"""Answers sent through a pipe; HOME is a temporary folder."""
		with tempfile.TemporaryDirectory() as home:
			result = subprocess.run(
				[str(ROOT / "42pal")], input="\npw\n2\n1\n\n\nstatus\nfinish\n",
				capture_output=True, text=True, timeout=30,
				env=dict(os.environ, HOME=home),
				# A new session has no terminal: nothing can wait on the keyboard.
				start_new_session=True,
			)
			self.assertEqual(result.returncode, 0, result.stderr)
			self.assertIn("Welcome", result.stdout)
			self.assertIn("End of the exam", result.stdout)
			self.assertEqual(len(list(Path(home).glob("42pal_exam/subjects/*/subject.en.txt"))), 1)
			if shutil.which("git"):
				# rendu/ is a git repository pushing to ~/.42pal/rendu.git.
				self.assertTrue((Path(home) / "42pal_exam/rendu/.git").is_dir())
				self.assertTrue((Path(home) / ".42pal/rendu.git").is_dir())

	def test_full_screen_only_in_a_real_terminal(self):
		"""--plain, or input that is not a terminal, gives the text interface."""
		from pal42.__main__ import full_screen
		self.assertFalse(full_screen(plain=True, stdin_tty=True, stdout_tty=True))
		self.assertFalse(full_screen(plain=False, stdin_tty=False, stdout_tty=True))
		self.assertFalse(full_screen(plain=False, stdin_tty=True, stdout_tty=False))
		self.assertTrue(full_screen(plain=False, stdin_tty=True, stdout_tty=True))

	def test_the_hard_option_is_gone(self):
		"""The mode is chosen in the menu now: --hard is refused."""
		result = subprocess.run([str(ROOT / "42pal"), "--hard"], capture_output=True, text=True)
		self.assertEqual(result.returncode, 2)

@unittest.skipUnless(hasattr(os, "fork"), "needs a pseudo-terminal (Linux, macOS)")
class TestRealTerminal(unittest.TestCase):
	"""./42pal in a pseudo-terminal: what a student really sees on the screen."""

	def test_enter_alone_goes_to_a_new_line(self):
		"""Enter with nothing typed: the next prompt starts on a new line."""
		with tempfile.TemporaryDirectory() as home:
			screen = run_in_terminal(home, [
				# Student, then the first of its exams (the Exam Rank 02).
				("login:", ""), ("password:", "x"), ("choice:", "2"), ("Exam:", "1"), ("Mode:", ""),
				("level:", ""), ("examshell>", ""), ("examshell>", "finish"),
			])
		self.assertNotIn("examshell> examshell>", screen)
		self.assertNotRegex(screen, "login:.*password:")
		self.assertIn("End of the exam", screen)

def run_in_terminal(home, steps, timeout=15):
	"""Run ./42pal in a pseudo-terminal; for each (prompt, answer), wait, then type.

	Returns everything the screen got, without the color codes. With a
	pseudo-terminal, readline and the echo behave as in a real terminal.
	"""
	pid, fd = pty.fork()
	if pid == 0:
		# The child: becomes ./42pal --plain (the text interface, line by
		# line), with HOME set to the temporary folder.
		os.environ["HOME"] = home
		os.execv(str(ROOT / "42pal"), ["42pal", "--plain"])
	screen = b""
	deadline = time.monotonic() + timeout

	def read_until(text):
		nonlocal screen
		start = len(screen)
		while text.encode() not in screen[start:] and time.monotonic() < deadline:
			if select.select([fd], [], [], 0.1)[0]:
				try:
					screen += os.read(fd, 4096)
				except OSError:
					return

	for prompt, answer in steps:
		read_until(prompt)
		os.write(fd, answer.encode() + b"\r")
	read_until("End of the exam")
	# A child still waiting for an answer the test did not give is stopped:
	# the test then fails on what the screen shows, instead of hanging.
	if os.waitpid(pid, os.WNOHANG) == (0, 0):
		os.kill(pid, signal.SIGKILL)
		os.waitpid(pid, 0)
	os.close(fd)
	return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", screen.decode(errors="replace")).replace("\r", "")

class TestGrademe(unittest.TestCase):
	"""grademe in the shell: grade, show the result and the trace, move on."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)

	def tearDown(self):
		self.tmp.cleanup()

	def start(self, level, *answers):
		"""A shell at `level` of the exam, which will read `answers`."""
		self.script = Script(*answers)
		shell = make_shell(self.script, self.root)
		shell.start(self.exam, level)
		return shell

	def hand_in(self, code):
		"""Write the student's echo_first.c in rendu/echo_first/."""
		(self.root / "rendu/echo_first/echo_first.c").write_text(code, encoding="utf-8")

	def test_right_solution_gives_ok_a_log_and_the_next_level(self):
		"""OK with 3/3, a log in traces/ shown with its path, then level 2."""
		shell = self.start(1, "grademe", "finish")
		self.hand_in(ECHO_OK)
		shell.command_loop()
		text = output(shell)
		self.assertIn("OK", text)
		self.assertIn("3/3", text)
		log = self.root / "traces/01_echo_first.trace"
		self.assertIn("OK", log.read_text(encoding="utf-8"))
		self.assertIn("traces/01_echo_first.trace", text)
		self.assertEqual(shell.level, 2)

	def test_last_playable_level_passed_ends_the_exam_below_100(self):
		"""Level 2 is the last playable one out of 4: 25/100, said honestly."""
		shell = self.start(2, "grademe")
		self.hand_in(ECHO_OK)
		shell.command_loop()
		text = output(shell)
		self.assertIn("No more playable level", text)
		self.assertNotIn("Exam passed", text)
		self.assertEqual(len(self.script.prompts), 1)

	def test_all_four_levels_passed_is_100_and_the_exam_is_passed(self):
		"""An exercise at every level: 4 OK in a row give 100/100."""
		themes = {"char_sets": Theme("char_sets", "Compare characters", {"rank02": (1, 2, 3, 4)})}
		self.exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=themes)
		shell = self.start(1, "grademe", "grademe", "grademe", "grademe")
		self.hand_in(ECHO_OK)
		shell.command_loop()
		text = output(shell)
		self.assertIn("grade 100/100", text)
		self.assertIn("Exam passed", text)

	def test_the_subject_panel_says_what_the_level_is_worth(self):
		"""Like 42_EXAM's "for 25 potential points": shown with the subject."""
		shell = self.start(1, "finish")
		self.assertIn("is worth 25 points", output(shell))

	def test_each_ok_gives_its_points_and_the_grade(self):
		"""OK at level 1 of 4: +25 points, grade 25/100, shown in status too."""
		shell = self.start(1, "grademe", "status", "finish")
		self.hand_in(ECHO_OK)
		shell.command_loop()
		text = output(shell)
		self.assertIn("+25 points · grade 25/100", text)
		self.assertRegex(text, r"Grade\s+25/100")

	def test_wrong_solution_shows_the_trace_and_keeps_the_subject(self):
		"""KO: the trace in the terminal and in traces/; same subject, same level."""
		shell = self.start(1, "grademe", "finish")
		subject = shell.variant
		self.hand_in(ECHO_OK.replace('\twrite(1, "\\n", 1);\n', ""))
		shell.command_loop()
		text = output(shell)
		self.assertIn("KO", text)
		self.assertIn("-hello", text)
		self.assertIn("Diff KO", text)
		# The 80-wide lines of the trace fit in its frame: none is cut in two.
		self.assertIn("= Test 1 " + "=" * 71, text)
		log = self.root / "traces/01_echo_first.trace"
		self.assertIn("Diff KO", log.read_text(encoding="utf-8"))
		self.assertEqual((shell.level, shell.variant), (1, subject))

	def test_long_trace_is_cut_on_screen_but_whole_in_the_file(self):
		"""60 wrong lines: the start on screen, a note, all of it in the file."""
		shell = self.start(1, "grademe", "finish")
		self.hand_in(
			"#include <unistd.h>\n\nint\tmain(void)\n{\n\tfor (int i = 0; i < 60; i++)\n"
			"\t\twrite(1, \"x\\n\", 2);\n\treturn (0);\n}\n"
		)
		shell.command_loop()
		self.assertIn("more lines", output(shell))
		log = self.root / "traces/01_echo_first.trace"
		self.assertEqual(log.read_text(encoding="utf-8").count("-x$"), 60)

	def test_the_animation_lasts_long_enough_to_be_seen_in_a_terminal(self):
		"""In a terminal, a quick grading still shows the spinner a moment."""
		pauses = []
		console = Console(file=io.StringIO(), width=100, force_terminal=True, color_system=None)
		shell = Shell(console, Script("grademe", "finish").ask, None, Workspace(self.root),
			rng=Random(1), clock=FakeClock(), sleep=pauses.append)
		shell.start(self.exam, 1)
		self.hand_in(ECHO_OK)
		shell.command_loop()
		self.assertGreater(sum(pauses), 0.5)

class TestGrademeWithLeaks(unittest.TestCase):
	"""grademe on an exercise that checks leaks."""

	def test_grade_result_shows_the_warnings(self):
		"""What could not be checked is said, under the verdict."""
		result = Grade(True, "", 3, 3, ("valgrind not found: memory leaks were not checked",))
		console = Console(file=io.StringIO(), width=100, color_system=None)
		console.print(display.grade_result(result, Path("/tmp/01_x.trace")))
		self.assertIn("valgrind not found", console.file.getvalue())

	@unittest.skipUnless(shutil.which("valgrind"), "valgrind is not installed")
	def test_grademe_checks_the_leaks_without_crashing(self):
		"""The spinner gets a third argument for the leak step: no crash, OK."""
		exo = make_exercise(
			name="echo_first", expected_files=("echo_first.c",),
			oracle=echo_oracle, generate_tests=echo_tests, check_leaks=True,
		)
		exam = load_exam("rank02", catalog=Catalog({"echo_first": exo}, []), themes=ECHO_THEMES)
		with tempfile.TemporaryDirectory() as tmp:
			root = Path(tmp) / "42pal_exam"
			shell = make_shell(Script("grademe"), root)
			shell.start(exam, 2)
			(root / "rendu/echo_first/echo_first.c").write_text(ECHO_OK, encoding="utf-8")
			shell.command_loop()
			self.assertIn("✓ OK", output(shell))

class TestCheckCatalog(unittest.TestCase):
	"""check_catalog(): every ref.c against its oracle, for the whole catalog."""

	def run_check(self, catalog=None, names=None):
		"""Run the check; return its exit code and what it printed."""
		console = Console(file=io.StringIO(), width=120, color_system=None)
		code = check.check_catalog(console, catalog, names)
		return code, console.file.getvalue()

	def test_only_the_exercises_named_are_checked(self):
		"""check-catalog echo_first: lonely, without its ref.c, is not looked at."""
		with tempfile.TemporaryDirectory() as lonely, tempfile.TemporaryDirectory() as echo:
			(Path(echo) / "ref.c").write_text(ECHO_OK, encoding="utf-8")
			catalog = Catalog({"lonely": make_exercise(name="lonely"), "echo_first": ECHO.exercise}, [],
				{"lonely": Path(lonely), "echo_first": Path(echo)})
			code, text = self.run_check(catalog, ["echo_first"])
			self.assertEqual(code, 0, text)
			self.assertIn("echo_first", text)
			self.assertNotIn("lonely", text)
			self.assertIn("Catalog OK: 1 exercises", text)
			code, text = self.run_check(catalog, ["nope"])
		self.assertEqual(code, 1)
		self.assertIn("Unknown exercise: nope", text)

	def test_wrong_oracle_fails_naming_the_variant_and_the_test(self):
		"""An oracle that shouts: exit code 1, broken#seed and the test named."""
		exo = make_exercise(
			name="broken", expected_files=("broken.c",),
			oracle=lambda params, test: echo_oracle(params, test).upper(),
			generate_tests=echo_tests,
		)
		with tempfile.TemporaryDirectory() as folder:
			(Path(folder) / "ref.c").write_text(ECHO_OK, encoding="utf-8")
			code, text = self.run_check(Catalog({"broken": exo}, [], {"broken": Path(folder)}))
		self.assertEqual(code, 1)
		self.assertRegex(text, r"broken#\d+")
		self.assertIn("= Test 1", text)
		self.assertIn("Catalog KO", text)

	def test_no_reference_at_all_says_a_git_clone_is_needed(self):
		"""A release archive leaves the ref.c out: one clear line, not one error per exercise."""
		with tempfile.TemporaryDirectory() as folder:
			catalog = Catalog({"echo_first": ECHO.exercise}, [], {"echo_first": Path(folder)})
			code, text = self.run_check(catalog)
		self.assertEqual(code, 1)
		self.assertIn("git clone", text)
		self.assertNotIn("no ref.c", text)

	def test_the_variants_of_an_exercise_are_graded_at_the_same_time(self):
		"""Two variants that wait for each other: graded one after the other, they block."""
		meeting = threading.Barrier(2, timeout=5)
		def graded_together(variant, ref):
			meeting.wait()
			return Grade(True, "", 1, 1)
		with tempfile.TemporaryDirectory() as folder:
			(Path(folder) / "ref.c").write_text(ECHO_OK, encoding="utf-8")
			catalog = Catalog({"pair": make_exercise(name="pair")}, [], {"pair": Path(folder)})
			with mock.patch.object(check, "check_variant", graded_together):
				code, text = self.run_check(catalog)
		self.assertEqual(code, 0, text)
		self.assertIn("2/2 variants OK", text)

	def test_missing_ref_c_and_catalog_warnings_fail(self):
		"""No ref.c for one exercise, or a folder skipped by the catalog: both are errors."""
		with tempfile.TemporaryDirectory() as lonely, tempfile.TemporaryDirectory() as echo:
			(Path(echo) / "ref.c").write_text(ECHO_OK, encoding="utf-8")
			catalog = Catalog({"lonely": make_exercise(name="lonely"), "echo_first": ECHO.exercise},
				["c/empty: no exercise.py, folder skipped"],
				{"lonely": Path(lonely), "echo_first": Path(echo)})
			code, text = self.run_check(catalog)
		self.assertEqual(code, 1)
		self.assertIn("lonely: no ref.c", text)
		self.assertIn("c/empty: no exercise.py", text)

class TestRetryTimer(unittest.TestCase):
	"""The wait between two grademe, with a rule of 0, 5, 10, 20, 40 minutes."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.clock = FakeClock()

	def tearDown(self):
		self.tmp.cleanup()

	def run_commands(self, *answers, code=None):
		"""Start at level 1, hand in `code` (wrong by default), run."""
		shell = make_shell(Script(*answers), self.root, self.clock)
		# Its own rule, so that these tests do not depend on the exam files.
		shell.retry = RetryPolicy((0, 5, 10, 20, 40))
		shell.start(self.exam, 1)
		(self.root / "rendu/echo_first/echo_first.c").write_text(
			code or "int\tmain(void)\n{\n\treturn (0);\n}\n", encoding="utf-8")
		shell.command_loop()
		return shell

	def logs(self):
		return sorted(path.name for path in (self.root / "traces").glob("*.trace"))

	def test_first_failure_is_free(self):
		"""After the first KO, grademe can run again at once."""
		shell = self.run_commands("grademe", "grademe", "finish")
		self.assertEqual(output(shell).count("✗ KO"), 2)
		self.assertEqual(self.logs(), ["01_echo_first.trace", "02_echo_first.trace"])

	def test_after_the_second_failure_grademe_must_wait(self):
		"""Second KO: 5 minutes to wait; a grademe before is refused, not counted."""
		shell = self.run_commands("grademe", "grademe", "grademe", "finish")
		text = output(shell)
		self.assertIn("Next grademe in 0:05:00", text)
		self.assertIn("if KO again: 0:10:00", text)
		self.assertIn("Wait 0:05:00 before your next grademe", text)
		self.assertEqual(len(self.logs()), 2)

	def test_grademe_works_again_once_the_wait_is_over(self):
		"""5 minutes later, the third grademe runs."""
		def five_minutes_later():
			self.clock.now += 300
			return "grademe"
		shell = self.run_commands("grademe", "grademe", five_minutes_later, "finish")
		self.assertEqual(len(self.logs()), 3)
		self.assertNotIn("Wait", output(shell))

	def test_each_grademe_warns_of_the_wait_if_it_fails(self):
		"""Before grading: what a KO would cost. First time: right away."""
		shell = self.run_commands("grademe", "grademe", "finish")
		text = output(shell)
		self.assertIn("If KO: next grademe right away", text)
		self.assertIn("If KO: next grademe in 0:05:00", text)

	def test_status_shows_the_next_grademe_and_the_cost_of_a_ko(self):
		"""After two KO: next grademe in 5 minutes, and 10 if the next one fails."""
		shell = self.run_commands("grademe", "grademe", "status", "finish")
		text = output(shell)
		self.assertRegex(text, r"Next grademe\s+in 0:05:00")
		self.assertRegex(text, r"If KO\s+0:10:00")

	def test_ok_resets_the_count_of_failures(self):
		"""KO, KO, then OK (5 minutes later): the next subject starts with no wait."""
		def fix_it_and_wait():
			self.clock.now += 300
			(self.root / "rendu/echo_first/echo_first.c").write_text(ECHO_OK, encoding="utf-8")
			return "grademe"
		shell = self.run_commands("grademe", "grademe", fix_it_and_wait, "status", "finish")
		self.assertEqual(shell.level, 2)
		self.assertEqual(shell.failures, 0)
		self.assertRegex(output(shell), r"Next grademe\s+now")

class TestExamTime(unittest.TestCase):
	"""The exam ends when its time is up (rank02: 180 minutes)."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.clock = FakeClock()

	def tearDown(self):
		self.tmp.cleanup()

	def later(self, minutes, command):
		"""An answer typed `minutes` later: the clock moves, then `command`."""
		def answer():
			self.clock.now += minutes * 60
			return command
		return answer

	def run_commands(self, *answers, code=ECHO_OK):
		self.script = Script(*answers)
		shell = make_shell(self.script, self.root, self.clock)
		shell.start(self.exam, 1)
		(self.root / "rendu/echo_first/echo_first.c").write_text(code, encoding="utf-8")
		shell.command_loop()
		return shell

	def test_time_up_ends_the_exam_at_the_next_command(self):
		"""181 minutes later, status is not run: time is up, the exam ends."""
		shell = self.run_commands(self.later(181, "status"), "help")
		text = output(shell)
		self.assertIn("Time is up", text)
		self.assertIn("End of the exam", text)
		self.assertNotIn("Time spent  ", text.split("Time is up")[0])
		self.assertEqual(len(self.script.prompts), 1)

	def test_grademe_after_the_time_is_up_is_not_graded(self):
		"""A right solution, but too late: not graded, no log."""
		shell = self.run_commands(self.later(200, "grademe"))
		self.assertIn("Time is up", output(shell))
		self.assertEqual(list((self.root / "traces").glob("*.trace")), [])
		self.assertEqual(shell.level, 1)

	def test_a_warning_once_when_less_than_ten_minutes_are_left(self):
		"""171 minutes in: one warning, not repeated at the next command."""
		shell = self.run_commands(self.later(171, "help"), self.later(1, "help"), "finish")
		self.assertEqual(output(shell).count("Less than 10 minutes left"), 1)

	def test_the_exam_time_keeps_running_across_levels(self):
		"""20 minutes, OK (level 2), 10 more minutes: 0:30:00 spent, not 0:10:00."""
		shell = self.run_commands(self.later(20, "grademe"), self.later(10, "finish"))
		self.assertEqual(shell.level, 2)
		self.assertRegex(output(shell), r"Time spent\s+0:30:00")

	def test_the_end_of_the_exam_shows_a_summary(self):
		"""One OK (level 1), then finish: levels passed, grademe, time spent."""
		shell = self.run_commands("grademe", self.later(30, "finish"))
		text = output(shell)
		self.assertIn("Summary", text)
		self.assertRegex(text, r"Levels passed\s+1")
		self.assertRegex(text, r"Grade\s+25/100")
		self.assertRegex(text, r"Grademe\s+1 \(1 OK, 0 KO\)")
		self.assertRegex(text, r"Time spent\s+0:30:00")

class TestSessionInShell(unittest.TestCase):
	"""The shell saves the exam in progress and keeps the finished ones."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.store = SessionStore(Path(self.tmp.name) / ".42pal")
		self.exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.clock = FakeClock()

	def tearDown(self):
		self.tmp.cleanup()

	def shell(self, *answers):
		console = Console(file=io.StringIO(), width=100, color_system=None)
		script = Script(*answers)
		return Shell(console, script.ask, script.ask_password, Workspace(self.root),
			rng=Random(1), clock=self.clock, sleep=lambda seconds: None,
			store=self.store, catalog=ECHO_CATALOG, themes=ECHO_THEMES)

	def test_the_exam_is_saved_after_start_and_after_each_command(self):
		"""After start, and after a grademe: level, subject and attempts saved."""
		seen = []
		def look_at_the_saved_exam():
			seen.append(self.store.load())
			return "finish"
		shell = self.shell("grademe", look_at_the_saved_exam)
		shell.start(self.exam, 1)
		self.assertEqual(self.store.load().variant, shell.variant.id)
		shell.command_loop()
		self.assertEqual((seen[0].level, seen[0].attempts, seen[0].failures), (1, 1, 1))

	def test_the_end_of_the_exam_goes_to_the_history_and_clears_the_session(self):
		"""grademe OK then finish: one entry in the history, nothing to resume."""
		shell = self.shell("grademe", "finish")
		shell.start(self.exam, 1)
		(self.root / "rendu/echo_first/echo_first.c").write_text(ECHO_OK, encoding="utf-8")
		shell.command_loop()
		self.assertIsNone(self.store.load())
		[entry] = self.store.history()
		self.assertEqual(entry["exam"], "rank02")
		self.assertEqual(entry["grade"], 25)
		self.assertEqual((entry["levels_passed"], entry["attempts"], entry["oks"]), ([1], 1, 1))
		self.assertEqual(entry["end"], "finish")

class TestResume(unittest.TestCase):
	"""./42pal again after the terminal was closed: resume the exam."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.store = SessionStore(Path(self.tmp.name) / ".42pal")
		self.clock = FakeClock()

	def tearDown(self):
		self.tmp.cleanup()

	def save(self, minutes_ago, variant="echo_first#5"):
		"""An exam of rank02 started `minutes_ago`, at level 2, saved."""
		self.store.save(Session(
			exam="rank02", level=2, variant=variant,
			started_at=self.clock.now - minutes_ago * 60, mode="exam",
			attempts=2, oks=1, failures=0, passed_levels=[1],
		))

	def run_shell(self, *answers):
		console = Console(file=io.StringIO(), width=100, color_system=None)
		self.script = Script(*answers)
		shell = Shell(console, self.script.ask, self.script.ask_password, Workspace(self.root),
			rng=Random(1), clock=self.clock, sleep=lambda seconds: None,
			store=self.store, catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		shell.run()
		return shell

	def test_enter_resumes_the_saved_exam(self):
		"""Same level, subject and mode; the time kept running while away."""
		self.save(10)
		shell = self.run_shell("", "pw", "", "status", "finish")
		self.assertTrue(any("Resume your exam?" in prompt for prompt in self.script.prompts))
		self.assertEqual((shell.level, shell.variant.id, shell.mode), (2, "echo_first#5", "exam"))
		text = output(shell)
		self.assertRegex(text, r"Time spent\s+0:10:00")
		self.assertRegex(text, r"Grademe\s+2 \(1 OK, 1 KO\)")

	def test_no_keeps_the_old_exam_in_the_history_and_starts_a_new_one(self):
		"""n: the old exam is "abandoned" in the history, a new exam starts."""
		self.save(10)
		# n, then the first menu: 1, the exams of the students.
		self.run_shell("", "pw", "n", "1", "", "", "finish")
		ends = [entry["end"] for entry in self.store.history()]
		self.assertEqual(ends, ["abandoned", "finish"])
		self.assertEqual(self.store.history()[0]["levels_passed"], [1])

	def test_an_exam_whose_time_ran_out_goes_to_the_history_without_asking(self):
		"""Started 200 minutes ago (180 allowed): kept as "time", no question."""
		self.save(200)
		shell = self.run_shell("", "pw", "1", "", "", "finish")
		self.assertIn("time ran out", output(shell))
		self.assertFalse(any("Resume" in prompt for prompt in self.script.prompts))
		self.assertEqual(self.store.history()[0]["end"], "time")

	def test_an_unknown_subject_cannot_be_resumed(self):
		"""The exercise is gone from the catalog: said, and a new exam starts."""
		self.save(10, variant="gone#3")
		shell = self.run_shell("", "pw", "1", "", "", "finish")
		self.assertIn("cannot be resumed", output(shell))
		self.assertEqual(shell.level, 1)

def git(*args, cwd):
	"""Run git in `cwd`; return the finished process (output as text)."""
	return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

@unittest.skipUnless(shutil.which("git"), "git is not installed")
class TestRenduGit(unittest.TestCase):
	"""rendu/ is a git repository: add, commit and push work, like at the exam."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.remote = Path(self.tmp.name) / ".42pal" / "rendu.git"
		self.variant = Variant(load_catalog().exercises["char_filter"], 0,
			{"mode": "common", "order": "ascii", "separator": "space"})

	def tearDown(self):
		self.tmp.cleanup()

	def test_add_commit_and_push_work_in_rendu(self):
		"""git add . && git commit && git push: the commit reaches the remote."""
		Workspace(self.root, remote=self.remote).give_subject(self.variant)
		rendu = self.root / "rendu"
		(rendu / "common_chars/common_chars.c").write_text("int\\tmain(void);\\n", encoding="utf-8")
		for args in [("add", "."), ("commit", "-m", "my work"), ("push",)]:
			result = git(*args, cwd=rendu)
			self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
		log = git("log", "--oneline", cwd=self.remote)
		self.assertIn("my work", log.stdout)

	def test_the_next_subject_keeps_the_repository_and_its_history(self):
		"""A second subject: no new git init, the first commit is still there."""
		workspace = Workspace(self.root, remote=self.remote)
		workspace.give_subject(self.variant)
		rendu = self.root / "rendu"
		(rendu / "common_chars/common_chars.c").write_text("int\tmain(void);\n", encoding="utf-8")
		git("add", ".", cwd=rendu)
		git("commit", "-m", "level 1", cwd=rendu)
		workspace.give_subject(Variant(self.variant.exercise, 1,
			{"mode": "only_first", "order": "ascii", "separator": "space"}))
		self.assertIn("level 1", git("log", "--oneline", cwd=rendu).stdout)
		self.assertEqual(git("remote", "get-url", "origin", cwd=rendu).stdout.strip(), str(self.remote))

	def test_without_git_rendu_is_a_plain_folder(self):
		"""git missing: no error, rendu/ is a plain folder (grademe still works)."""
		Workspace(self.root, remote=self.remote, git="no_such_git").give_subject(self.variant)
		self.assertTrue((self.root / "rendu/common_chars").is_dir())
		self.assertFalse((self.root / "rendu/.git").exists())

class TestCompletion(unittest.TestCase):
	"""Tab completes the examshell commands (readline calls complete_command)."""

	def test_tab_completes_a_command_from_its_start(self):
		"""gr gives grademe, then nothing more; x gives nothing."""
		self.assertEqual(complete_command("gr", 0), "grademe")
		self.assertIsNone(complete_command("gr", 1))
		self.assertIsNone(complete_command("x", 0))

	def test_tab_on_nothing_lists_every_command(self):
		"""readline asks again and again (state 0, 1, 2...) until None."""
		found = []
		state = 0
		while (command := complete_command("", state)) is not None:
			found.append(command)
			state += 1
		self.assertCountEqual(found, ["status", "grademe", "report", "finish", "help"])

class TestPractice(unittest.TestCase):
	"""./42pal practice: subjects of one theme, no timer, no wait."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"

	def tearDown(self):
		self.tmp.cleanup()

	def practise(self, *answers, code=None, theme="char_sets"):
		"""Practise `theme`, with `code` handed in once the first subject is given."""
		console = Console(file=io.StringIO(), width=100, color_system=None)
		self.script = Script(*answers)
		shell = PracticeShell(console, self.script.ask, Workspace(self.root), rng=Random(1),
			catalog=ECHO_CATALOG, themes=ECHO_THEMES, sleep=lambda seconds: None)
		if code:
			rendu = self.root / "rendu/echo_first"
			rendu.mkdir(parents=True)
			(rendu / "echo_first.c").write_text(code, encoding="utf-8")
		shell.run(theme)
		return shell

	def test_with_two_languages_the_language_is_asked_first(self):
		"""C and Python themes: the language menu, then the themes of that language only."""
		console = Console(file=io.StringIO(), width=100, color_system=None)
		python_exo = make_exercise(name="py_echo", language="python", allowed_functions=(),
			themes=("py_sets",), expected_files=("py_echo.py",))
		catalog = Catalog({"echo_first": ECHO.exercise, "py_echo": python_exo}, [])
		themes = dict(ECHO_THEMES, py_sets=Theme("py_sets", "Compare in Python", {"rank03": (1,)}))
		# 2: Python; 2: back from its themes; 1: C; 1: its only theme.
		script = Script("2", "2", "1", "1", "finish")
		shell = PracticeShell(console, script.ask, Workspace(self.root), rng=Random(1),
			catalog=catalog, themes=themes, sleep=lambda seconds: None)
		shell.run()
		text = output(shell)
		self.assertIn("1. C (1 theme)", text)
		self.assertIn("2. Python (1 theme)", text)
		self.assertIn("1. py_sets · Compare in Python", text)
		self.assertIn("2. Back (previous menu)", text)
		self.assertEqual(text.count("Choose a language:"), 2)
		self.assertEqual(shell.variant.exercise.name, "echo_first")

	def test_a_subject_of_the_theme_with_no_login_and_no_timer(self):
		"""The subject is given at once: no login, no time left anywhere."""
		shell = self.practise("finish")
		text = output(shell)
		self.assertIn("Practice · char_sets", text)
		self.assertIn("Assignment name  : echo_first", text)
		self.assertNotIn("login:", self.script.prompts)
		self.assertNotIn("Time left", text)

	def test_ok_moves_to_another_subject_of_the_theme(self):
		"""A passed grademe gives the next subject of the same theme."""
		shell = self.practise("grademe", "finish", code=ECHO_OK)
		self.assertEqual(output(shell).count("Practice · char_sets"), 2)
		self.assertEqual((shell.passed, len(shell.seen)), (1, 2))

	def test_no_wait_between_two_failures(self):
		"""Three KO in a row: all three are graded."""
		shell = self.practise("grademe", "grademe", "grademe", "finish",
			code="int\\tmain(void)\\n{\\n\\treturn (0);\\n}\\n")
		self.assertEqual(output(shell).count("✗ KO"), 3)
		self.assertNotIn("Wait", output(shell))

	def test_next_gives_another_subject(self):
		"""next: a new subject of the theme, without grading."""
		shell = self.practise("next", "finish")
		self.assertEqual(len(shell.seen), 2)

	def test_without_a_theme_a_menu_lists_the_themes_that_have_exercises(self):
		"""No theme given: a numbered menu with each theme's skill, then practice."""
		shell = self.practise("1", "finish", theme=None)
		text = output(shell)
		self.assertIn("1. char_sets · Compare characters", text)
		self.assertIn("Practice · char_sets", text)

	def test_one_letter_shortcuts_and_handle(self):
		"""n for next, ? for help, f for finish: handle says when it is over."""
		shell = self.practise("n", "?", "f")
		text = output(shell)
		self.assertEqual(text.count("Practice · char_sets"), 2)
		self.assertIn("another subject of the same theme", text)
		self.assertIn("Practice summary", text)

	def test_the_last_choice_of_the_theme_menu_quits(self):
		"""2 after the only theme: goodbye, no subject."""
		shell = self.practise("2", theme=None)
		text = output(shell)
		self.assertIn("2. Quit", text)
		self.assertIn("Goodbye!", text)
		self.assertNotIn("Practice ·", text)

	def test_an_unknown_theme_lists_the_themes_that_can_be_practised(self):
		"""A theme with no exercise (or a typo): said, with the ones that work."""
		console = Console(file=io.StringIO(), width=100, color_system=None)
		shell = PracticeShell(console, Script().ask, Workspace(self.root),
			catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.assertEqual(shell.run("words"), 1)
		self.assertIn("No exercise to practise 'words' yet. Themes: char_sets", output(shell))

	def test_finish_shows_how_it_went(self):
		"""finish: the subjects passed and the grademe made."""
		shell = self.practise("grademe", "finish", code=ECHO_OK)
		self.assertIn("Practice summary: 1 subject passed, 1 grademe", output(shell))

class TestRevisionMode(unittest.TestCase):
	"""Revision mode: no time limit, the saved exam never runs out."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.clock = FakeClock()

	def tearDown(self):
		self.tmp.cleanup()

	def test_ten_hours_later_the_revision_goes_on(self):
		"""No end of exam in revision mode: status still answers 10 hours later."""
		def ten_hours_later():
			self.clock.now += 10 * 3600
			return "status"
		shell = make_shell(Script(ten_hours_later, "finish"), self.root, self.clock)
		shell.mode = "revision"
		shell.start(load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES), 1)
		shell.command_loop()
		self.assertNotIn("Time is up", output(shell))
		self.assertRegex(output(shell), r"Time spent\s+10:00:00")

	def test_a_saved_revision_does_not_run_out_while_away(self):
		"""Saved 10 hours ago in revision mode: it can still be resumed."""
		store = SessionStore(Path(self.tmp.name) / ".42pal")
		store.save(Session(exam="rank02", level=1, variant="echo_first#5",
			started_at=self.clock.now - 10 * 3600, mode="revision",
			attempts=0, oks=0, failures=0))
		console = Console(file=io.StringIO(), width=100, color_system=None)
		script = Script("", "pw", "", "finish")
		shell = Shell(console, script.ask, script.ask_password, Workspace(self.root),
			rng=Random(1), clock=self.clock, sleep=lambda seconds: None,
			store=store, catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		shell.run()
		self.assertEqual((shell.mode, shell.variant.id), ("revision", "echo_first#5"))
		self.assertTrue(any("no time limit" in prompt for prompt in script.prompts))

class FakeCheck:
	"""An update check that already knows its answer."""

	def __init__(self, update):
		self.update = update

	def result(self, wait=3):
		return self.update

class TestUpdateOffer(unittest.TestCase):
	"""After the login, the update found at launch is offered."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"

	def tearDown(self):
		self.tmp.cleanup()

	def run_offer(self, *answers, update=Update(2, ("feat: add a", "fix: repair b")), pulled=(True, "")):
		shell = make_shell(Script(*answers), self.root)
		shell.update_check = FakeCheck(update)
		self.pulls = []
		shell.updater = lambda: self.pulls.append(1) or pulled
		shell.run()
		return shell

	def test_yes_pulls_and_asks_for_a_restart(self):
		shell = self.run_offer("", "pw", "")
		text = output(shell)
		self.assertIn("A new version of 42pal is available: 2 new commits", text)
		self.assertIn("feat: add a", text)
		self.assertEqual(self.pulls, [1])
		self.assertTrue(shell.restart)

	def test_no_goes_on_with_this_version(self):
		shell = self.run_offer("", "pw", "n")
		self.assertEqual(self.pulls, [])
		self.assertFalse(shell.restart)
		self.assertIn("What do you want to do?", output(shell))

	def test_a_failed_pull_is_said_and_42pal_goes_on(self):
		shell = self.run_offer("", "pw", "y", pulled=(False, "error: your local changes"))
		self.assertIn("The update failed: error: your local changes", output(shell))
		self.assertFalse(shell.restart)

	def test_nothing_new_asks_nothing(self):
		shell = self.run_offer("", "pw", update=None)
		self.assertNotIn("new version", output(shell))

class TestSubjectText(unittest.TestCase):
	"""On the screen, what changes from a variant to another stands out."""

	def test_the_texts_of_the_params_are_styled_even_cut_by_the_wrapping(self):
		from pal42.catalog import load_catalog
		exo = load_catalog().exercises["word_pick"]
		variant = Variant(exo, 0, {"which": "longest", "how": "upper"})
		text = display.subject_text(variant, render(variant))
		styled = [" ".join(text.plain[span.start:span.end].split()) for span in text.spans]
		self.assertIn("its longest word (the first of them if several are as long)", styled)
		self.assertIn("with its lowercase letters turned into uppercase", styled)
		# The header and the examples stay as they are.
		self.assertFalse(any("Assignment" in part or "$>" in part for part in styled))

class TestDrivenShell(unittest.TestCase):
	"""The shell driven one command at a time, as the full-screen interface does."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.store = SessionStore(Path(self.tmp.name) / ".42pal")
		self.clock = FakeClock()
		console = Console(file=io.StringIO(), width=100, color_system=None)
		self.shell = Shell(console, Script().ask, Script().ask_password, Workspace(self.root),
			rng=Random(1), clock=self.clock, sleep=lambda seconds: None,
			store=self.store, catalog=ECHO_CATALOG, themes=ECHO_THEMES)

	def tearDown(self):
		self.tmp.cleanup()

	def test_begin_starts_an_exam_without_any_menu(self):
		"""begin(exam, mode, level): the subject is given, the waits follow the mode."""
		exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.shell.begin(exam, "revision", 2)
		self.assertEqual((self.shell.level, self.shell.mode), (2, "revision"))
		self.assertEqual(self.shell.retry, exam.retry["soft"])
		self.assertIn("Assignment name  : echo_first", output(self.shell))

	def test_handle_runs_one_command_and_tells_when_the_exam_is_over(self):
		"""status goes on; finish ends the exam and says so."""
		exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.shell.begin(exam, "exam", 1)
		self.assertFalse(self.shell.handle("status"))
		self.assertRegex(output(self.shell), r"Level\s+1 of 4")
		self.assertTrue(self.shell.handle("finish"))
		self.assertIn("End of the exam", output(self.shell))

	def test_one_letter_shortcuts(self):
		"""g, s, r, f and ? stand for grademe, status, report, finish and help."""
		exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		self.shell.begin(exam, "revision", 1)
		self.shell.handle("?")
		self.assertIn("grade your work", output(self.shell))
		self.shell.handle("s")
		self.assertRegex(output(self.shell), r"Subject\s+echo_first")
		self.shell.handle("g")
		self.assertIn("Missing file", output(self.shell))
		self.shell.handle("r")
		self.assertIn("Report written", output(self.shell))
		self.assertTrue(self.shell.handle("f"))

	def test_a_saved_exam_is_restored_then_resumed_or_abandoned(self):
		"""restore_saved puts it back; abandon_saved keeps it in the history."""
		self.store.save(Session(
			exam="rank02", level=2, variant="echo_first#5", started_at=self.clock.now - 600,
			mode="exam", attempts=2, oks=1, failures=0, passed_levels=[1],
		))
		self.assertTrue(self.shell.restore_saved())
		self.assertEqual((self.shell.level, self.shell.variant.id), (2, "echo_first#5"))
		self.shell.abandon_saved()
		self.assertEqual(self.store.history()[0]["end"], "abandoned")
		self.assertIsNone(self.shell.exam)
		self.assertFalse(self.shell.restore_saved())
