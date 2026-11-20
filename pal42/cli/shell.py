"""The examshell: fake login, choice of the exam and level, then commands.

Its input and output are given to it (ask, ask_password, console), so the
tests can drive it with answers written in advance; main() gives it the real
keyboard and terminal.
"""

import getpass
import math
import random
import sys
import time
from datetime import datetime

from rich.console import Console
from rich.markup import escape

from pal42 import cheat
from pal42.catalog import load_catalog
from pal42.cli import display
from pal42.cli.workspace import Workspace
from pal42.exam import AUDIENCES, ExamError, list_exams, load_exam
from pal42.grader import grade
from pal42.retry import RetryPolicy
from pal42.runners import runner_for
from pal42.progress import exam_rows, summary, weak_themes
from pal42.report import full_report
from pal42.session import STATE_DIR, Session, SessionStore
from pal42.themes import load_themes
from pal42.update import apply_update, restart

# The examshell commands and what they do, shown by help.
COMMANDS = {
	"status": "where you are: exam, level, subject, time",
	"grademe": "grade your work",
	"report": "write a report for an issue: subject, your code, last trace",
	"finish": "end the exam",
	"help": "show this help",
}

# One letter (then Enter) for each command: g, s, r, f and ?.
SHORTCUTS = {"g": "grademe", "s": "status", "r": "report", "f": "finish", "?": "help"}

# The two modes and the waits each one takes from the exam file: the exam
# mode is 42_EXAM's (hard waits, the real duration), the revision mode is
# softer (soft waits, no time limit).
RETRY_OF_MODE = {"exam": "hard", "revision": "soft"}

# Under this many seconds left, the student is warned once.
WARNING_SECONDS = 10 * 60

# The grademe spinner stays at least this long, even if the grading is quicker.
ANIMATION_SECONDS = 0.8

def make_completer(commands):
	"""Return readline's completer for `commands`.

	readline calls it with the text typed and state 0, 1, 2... until it
	returns None, then completes (one match) or lists the matches (several).
	"""
	def complete(text, state):
		matches = [command for command in commands if command.startswith(text)]
		return matches[state] if state < len(matches) else None
	return complete

# The completer of the examshell commands.
complete_command = make_completer(COMMANDS)

# What a menu returns when its last choice is picked: back to the menu before,
# or quit when it is the first menu shown.
BACK = object()

# The choices of the first menu that lead to practice, or to the progress, instead of an exam.
PRACTICE = "practice"
PROGRESS = "progress"

class Shell:
	"""One exam session in the terminal.

	ask(prompt, default) returns what the student types, ask_password(prompt)
	reads without showing it, and console is a rich Console. clock gives the
	time in seconds since 1970, so that a saved exam can be resumed later.
	store (a SessionStore) saves the exam in progress and the history; with
	None, nothing is saved. catalog and themes are loaded when not given.
	"""

	def __init__(self, console, ask, ask_password, workspace=None, rng=None,
			clock=time.time, sleep=time.sleep, mode="exam",
			store=None, catalog=None, themes=None):
		self.console = console
		self.ask = ask
		self.ask_password = ask_password
		self.workspace = workspace or Workspace()
		self.rng = rng or random.Random()
		self.clock = clock
		# For the typewriter animation; the tests give one that does not wait.
		self.sleep = sleep
		self.user = None
		# How many menus have been shown: tells choose_start which ones were.
		self.menus_shown = 0
		# "exam" or "revision", chosen in a menu by run().
		self.mode = mode
		self._reset()
		self.store = store
		self.catalog = catalog
		self.themes = themes
		# The check for a newer 42pal started at launch (an UpdateCheck), the
		# function that pulls it, and True once pulled: 42pal must restart.
		self.update_check = None
		self.updater = apply_update
		self.restart = False
		# The encrypted cheat menu: cheat.PACK unless a test gives its own.
		self.cheat_pack = None

	def _reset(self):
		"""No exam in progress: the state before an exam starts."""
		# Set by start(): the exam, the level, the subject and when it began.
		self.exam = None
		self.level = None
		self.variant = None
		self.started_at = None
		# Number of grademe so far: it numbers the logs in traces/.
		self.attempts = 0
		# The waits after a failure, the failures on the current subject, and
		# when grademe is allowed again.
		self.retry = RetryPolicy((0,))
		self.failures = 0
		self.next_grademe_at = None
		# For the summary: the levels passed and the grademe that passed.
		self.passed_levels = []
		self.oks = 0
		# True once the "less than 10 minutes" warning has been given.
		self.warned = False
		# True once the cheat menu was used: the history says so.
		self.cheated = False
		# The last trace written by grademe, and the last report written.
		self.last_trace = None
		self.last_report = None

	def run(self):
		"""The whole session: login, exam (or the saved one), then the commands."""
		try:
			self.login()
			if self.offer_update():
				return
			if not self.resume():
				start = self.choose_start()
				while start in (PRACTICE, PROGRESS):
					theme = self.show_progress() if start == PROGRESS else None
					if (start == PRACTICE or theme is not None) and self.practise(theme):
						return
					start = self.choose_start()
				if start is None:
					self.console.print("Goodbye!")
					return
				self.begin(*start)
		# Ctrl-D before the exam has started: just leave.
		except EOFError:
			self.console.print("\nGoodbye!")
			return
		self.command_loop()

	def login(self):
		"""Fake login, like at the exam: any password, never checked or kept."""
		display.typewriter(self.console, "42pal · examshell", sleep=self.sleep)
		self.user = self.ask("login:", getpass.getuser())
		# The password is read, then dropped at once: not checked, not stored.
		self.ask_password("password: ")
		display.typewriter(self.console, f"Welcome {self.user}!", sleep=self.sleep)
		self.console.print()

	def offer_update(self):
		"""Offer the newer 42pal found at launch; return True once pulled (to restart)."""
		update = self.update_check.result() if self.update_check else None
		if update is None:
			return False
		self.console.print(display.update_message(update))
		if self.ask("Update now?", "y").strip().lower().startswith("n"):
			self.console.print()
			return False
		ok, why = self.updater()
		if not ok:
			self.console.print(display.update_failed(why))
			self.console.print()
			return False
		self.console.print("42pal is updated: it starts again.")
		self.restart = True
		return True

	def resume(self):
		"""Offer to resume the saved exam; return True if it was resumed.

		Refusing keeps it in the history as "abandoned".
		"""
		if not self.restore_saved():
			return False
		question = display.resume_question(self.exam, self.level, self.variant, self._time_left())
		if self.ask(question, "y").strip().lower().startswith("n"):
			self.abandon_saved()
			return False
		self.show_subject()
		return True

	def restore_saved(self):
		"""Put back the saved exam, if there is one to resume; return True then.

		An exam whose time ran out while away goes to the history without a
		question; one whose subject is gone cannot be resumed. Both are said.
		"""
		session = self.store.load() if self.store else None
		if session is None:
			return False
		catalog, themes = self._catalog()
		try:
			exam = load_exam(session.exam, catalog=catalog, themes=themes)
		except ExamError:
			exam = None
		variant = catalog.variant(session.variant)
		if exam is None or variant is None:
			self.store.clear()
			self.console.print(display.cannot_resume(session.variant))
			return False
		self._restore(session, exam, variant)
		if self._time_left() <= 0:
			self.console.print(display.time_ran_out_while_away(exam))
			self._forget("time")
			return False
		return True

	def abandon_saved(self):
		"""Give up the restored exam: kept in the history as "abandoned"."""
		self._forget("abandoned")

	def _restore(self, session, exam, variant):
		"""Put back the state of a saved exam."""
		self.exam, self.level, self.variant = exam, session.level, variant
		self.started_at = session.started_at
		self.mode = session.mode
		self.retry = exam.retry[RETRY_OF_MODE[session.mode]]
		self.attempts, self.oks, self.failures = session.attempts, session.oks, session.failures
		self.passed_levels = list(session.passed_levels)
		self.next_grademe_at = session.next_grademe_at
		self.warned = session.warned
		self.cheated = session.cheat

	def _forget(self, end):
		"""Keep the restored exam in the history as `end`, then start afresh."""
		elapsed = self.clock() - self.started_at
		if self.mode == "exam":
			elapsed = min(elapsed, self.exam.duration_minutes * 60)
		self.store.add_history(self._history_entry(end, elapsed))
		self.store.clear()
		self._reset()

	def choose_start(self):
		"""The menus before an exam: who, which exam, which mode, which level.

		The last choice of each menu goes back to the menu before it; in the
		first menu shown, it quits. A step that needs no menu (a single exam,
		the level in exam mode) is skipped again on the way back. Return
		(exam, mode, level), PRACTICE when practice is chosen in the first
		menu, or None to quit.
		"""
		steps = [
			lambda chosen, first: self.choose_audience(first),
			lambda chosen, first: self.choose_exam(chosen[0], first),
			lambda chosen, first: self.choose_mode(chosen[1], first),
			lambda chosen, first: self.choose_level(chosen[1], chosen[2], first),
		]
		chosen = []
		# For each answer in chosen: True if a menu was shown to get it.
		shown = []
		while len(chosen) < len(steps):
			menus_before = self.menus_shown
			answer = steps[len(chosen)](chosen, not any(shown))
			if answer is BACK:
				if not any(shown):
					return None
				# Undo the answers up to the last menu shown, that one included.
				while not shown.pop():
					chosen.pop()
				chosen.pop()
				continue
			if answer in (PRACTICE, PROGRESS):
				return answer
			chosen.append(answer)
			shown.append(self.menus_shown > menus_before)
		_, exam, mode, level = chosen
		return exam, mode, level

	def choose_audience(self, first=True):
		"""The first menu: "piscine" or "student" (their exams), or PRACTICE; or BACK.

		Asked only when there is more than one choice.
		"""
		by_audience = {}
		for exam in self._exams():
			by_audience.setdefault(exam.audience, []).append(exam)
		by_audience = {audience: by_audience[audience] for audience in AUDIENCES
			if audience in by_audience}
		choices = list(by_audience) + ([PRACTICE] if self._can_practise() else [])
		choices += [PROGRESS] if self.store and self.store.grades() else []
		if len(choices) == 1:
			return choices[0]
		self._print_lines(display.audience_menu(by_audience, first, practice=PRACTICE in choices,
			progress=PROGRESS in choices))
		last = len(choices) + 1
		number = self._ask_choice("Your choice:", range(1, last + 1))
		self.console.print()
		return BACK if number == last else choices[number - 1]

	def _can_practise(self):
		"""Practice is offered when the catalog has exercises."""
		return bool(self._catalog()[0].exercises)

	def show_progress(self):
		"""The progress: a summary, the exams, then the weak themes; return the one to practise, or None.

		None: Back, to the first menu.
		"""
		history, grades = self.store.history(), self.store.grades()
		self.console.print(display.progress_summary(summary(history, grades)))
		rows = exam_rows(history)
		if rows:
			self.console.print(display.exam_progress_table(rows))
		weak = weak_themes(grades)
		_, themes = self._catalog()
		items = [(row.theme, row.theme, display.theme_score(row), themes[row.theme].skill if row.theme in themes else "")
			for row in weak if row.theme in themes]
		if not items:
			self.console.print("No weak theme: every theme you met passed its last grademe.")
			return None
		value = self._numbered_menu(("Practise a weak theme:", items), first=False)
		return None if value is BACK else value

	def practise(self, theme=None):
		"""Practice, chosen in the first menu: True once it is over, False after Back.

		The practice shell takes over with the same terminal and workspace;
		with a theme (from the progress), it starts on that theme at once.
		"""
		# Imported here: pal42.cli.practice imports this module.
		from pal42.cli.practice import PRACTICE_COMMANDS, PracticeShell
		catalog, themes = self._catalog()
		practice = PracticeShell(self.console, self.ask, self.workspace, rng=self.rng,
			catalog=catalog, themes=themes, sleep=self.sleep, store=self.store)
		complete_with(PRACTICE_COMMANDS)
		if practice.run(theme, first=False) is BACK:
			complete_with(COMMANDS)
			return False
		return True

	def choose_exam(self, audience, first=False):
		"""Show the exams of `audience` as a numbered menu; return the one picked, or BACK.

		A single exam is taken without asking, and said.
		"""
		exams = [exam for exam in self._exams() if exam.audience == audience]
		if len(exams) == 1:
			exam = exams[0]
			self.console.print(f"Your exam: {exam.title} ({display.exam_summary(exam)})")
			self.console.print()
			return exam
		self._print_lines(display.exam_menu(exams, first))
		last = len(exams) + 1
		number = self._ask_choice("Exam:", range(1, last + 1))
		self.console.print()
		return BACK if number == last else exams[number - 1]

	def choose_mode(self, exam, first=False):
		"""Ask the mode: "exam" (hard waits, the real duration) or "revision", or BACK."""
		self._print_lines(display.mode_menu(exam, first))
		# Enter alone takes revision.
		number = self._ask_choice("Mode:", [1, 2, 3], "2")
		self.console.print()
		return {1: "exam", 2: "revision", 3: BACK}[number]

	def choose_level(self, exam, mode="revision", first=False):
		"""Ask the starting level in revision mode; return it, or BACK.

		Exam mode starts at the first level, like the real exam: no question.
		"""
		playable = exam.playable_levels
		if mode == "exam":
			self.console.print(f"Exam mode starts at level {playable[0]}, like the real exam.")
			return playable[0]
		self._print_lines(display.level_menu(exam, first))
		last = exam.level_count + 1
		# Enter alone takes the first playable level.
		level = self._ask_choice("Starting level:", [*playable, last], str(playable[0]))
		if level == last:
			self.console.print()
			return BACK
		return level

	def _exams(self):
		"""The exams that can be played: those with exercises at one level at least."""
		catalog, themes = self._catalog()
		exams = [load_exam(exam_id, catalog=catalog, themes=themes) for exam_id in list_exams()]
		return [exam for exam in exams if exam.playable_levels]

	def _print_lines(self, lines):
		"""Print the lines of a menu as they are: no rich markup is read in them."""
		for line in lines:
			self.console.print(line, markup=False, highlight=False)

	def begin(self, exam, mode, level):
		"""Start an exam in `mode` ("exam" or "revision") at `level`, without menus."""
		self.mode = mode
		self.retry = exam.retry[RETRY_OF_MODE[mode]]
		self.start(exam, level)

	def start(self, exam, level):
		"""Draw a subject at `level`, write it in the workspace and show it.

		The exam's clock starts with the first subject only: passing a level
		does not give more time.
		"""
		self.exam = exam
		self.level = level
		self.variant = exam.draw(level, self.rng)
		if self.started_at is None:
			self.started_at = self.clock()
		self.show_subject()
		self._save()

	def show_subject(self):
		"""Write the current subject in the workspace and show it."""
		exam, level = self.exam, self.level
		subject = self.workspace.give_subject(self.variant)
		rendu = self.workspace.rendu / self.variant.name
		# First the panel (where to read and hand in), then the subject as
		# plain text: markup=False so that rich changes nothing, and no frame,
		# so that the examples can be copied as they are.
		self.console.print()
		self.console.print(display.subject_panel(
			exam, level, self.variant, subject, rendu, self.mode,
		))
		self.console.print()
		# The words of the variant stand out; rich reads no markup in a Text.
		self.console.print(display.subject_text(self.variant, subject.read_text(encoding="utf-8")), end="")
		self.console.print()

	def command_loop(self):
		"""Read and run the examshell commands until the exam ends.

		It ends with finish, Ctrl-D, the last level passed, or when the time
		is up: the time is checked each time a command is typed, so a command
		typed too late is not run.
		"""
		while True:
			try:
				command = self.ask("examshell>").strip()
			# Ctrl-D: the same as finish.
			except EOFError:
				command = "finish"
			if self.handle(command):
				return

	def handle(self, command):
		"""Run one examshell command; return True when the exam is over.

		The time is checked first: a command typed too late is not run.
		"""
		command = SHORTCUTS.get(command.strip(), command.strip())
		left = self._time_left()
		if left <= 0:
			self.console.print(display.time_up())
			self.end_exam("time")
			return True
		if left < WARNING_SECONDS and not self.warned:
			self.warned = True
			self.console.print(display.almost_over(left))
		if command == "finish":
			self.end_exam()
			return True
		if command == "help":
			self.console.print(display.help_table(COMMANDS))
		elif command == "status":
			self.show_status()
		elif command == "grademe":
			if self.grademe():
				return True
		elif command == "report":
			self.write_report()
		elif command == "cheat":
			# Hidden: in no help nor completion, for the owner of 42pal only.
			if self.cheat():
				return True
		elif command:
			# escape: what the student typed must not be read as rich markup.
			self.console.print(f"Unknown command: {escape(command)}. Type help for the list.")
		# A blank line after each answer sets it apart from the next prompt;
		# Enter alone gave no answer, so it adds nothing.
		if command:
			self.console.print()
		self._save()
		return False

	def grademe(self):
		"""Grade the rendu and show the result; return True when the exam is over.

		Passed: the next playable level, with a new subject, or the end of the
		exam after the last one. Failed: the trace, the same subject, and a
		wait before the next grademe that grows with each failure.
		"""
		wait = self._wait_left()
		if wait > 0:
			# Too early: refused, and not counted as an attempt.
			self.console.print(display.wait_message(wait))
			return False
		# What a KO would cost, said before grading.
		self.console.print(display.retry_preview(self.retry.wait_after(self.failures + 1)))
		result = self._grade_and_show(self.exam.compile_command)
		if not result.passed:
			self.failures += 1
			wait = self.retry.wait_after(self.failures)
			self.next_grademe_at = self.clock() + wait
			self.console.print(display.next_grademe(wait, self.retry.wait_after(self.failures + 1)))
			return False
		return self._level_passed()

	def _level_passed(self):
		"""The current level is passed: its points, then the next level or the end.

		Return True when the exam is over.
		"""
		# Passed: the next subject starts with no failure and no wait.
		self.failures = 0
		self.next_grademe_at = None
		self.oks += 1
		self.passed_levels.append(self.level)
		self.console.print(display.points_won(self.exam.points_per_level, self.grade))
		if self.grade >= 100:
			self.console.print(display.exam_passed_panel(self.exam))
			self.end_exam("passed")
			return True
		next_levels = [level for level in self.exam.playable_levels if level > self.level]
		if not next_levels:
			# The next levels have no exercise yet: the exam stops below 100.
			self.console.print(display.no_more_levels(self.grade))
			self.end_exam("no more levels")
			return True
		self.start(self.exam, next_levels[0])
		return False

	def _grade_and_show(self, compile_command):
		"""Grade the current subject's rendu, show the result; return the Grade.

		A spinner while grading, then OK or KO with the clickable log (written
		in traces/ at each grademe), then the trace of a failure.
		"""
		self.attempts += 1
		rendu = self.workspace.rendu / self.variant.name
		# The language of the subject: practice has no exam, only a subject.
		runner = runner_for(self.variant.exercise.language, compile_command)
		# A spinner while grading, with the number of the test being run.
		with self._status("Grading…") as status:
			# step is "memory" when the tests run again under valgrind.
			def progress(number, total, step="output"):
				doing = "Checking memory" if step == "memory" else "Grading"
				status.update(f"{doing}… test {number}/{total}")
			started = self.clock()
			result = grade(self.variant, rendu, runner, progress)
			# A grading often takes a tenth of a second: the spinner stays a
			# moment, so that it can be seen. Only in a real terminal.
			left = ANIMATION_SECONDS - (self.clock() - started)
			if self.console.is_terminal and left > 0:
				self.sleep(left)
		log_text = result.trace or f"OK: {result.tests_passed}/{result.tests_total} tests passed\n"
		log = self.workspace.write_trace(self.attempts, self.variant.name, log_text)
		self.last_trace = log
		self._keep_grade(result.passed)
		self.console.print(display.grade_result(result, log))
		if not result.passed:
			self.console.print(display.trace_panel(result.trace))
		return result

	def _keep_grade(self, passed):
		"""Keep this grademe in grades.json, for the progress: the subject, its themes, OK or KO."""
		if not self.store:
			return
		exo = self.variant.exercise
		self.store.add_grade({
			"when": datetime.fromtimestamp(self.clock()).isoformat(timespec="seconds"),
			"variant": self.variant.id,
			"exercise": exo.name,
			"themes": list(exo.themes),
			"language": exo.language,
			"passed": passed,
			"source": self.exam.id if self.exam else "practice",
			**({"cheat": True} if self.cheated else {}),
		})

	def _status(self, text):
		"""The spinner shown while grading: rich shows it only in a real terminal.

		It returns a context manager whose update(text) changes the text; the
		full-screen interface puts its own instead.
		"""
		return self.console.status(text, spinner="dots")

	@property
	def grade(self):
		"""The grade out of 100: the points of each level passed, like 42_EXAM."""
		return self.exam.points_per_level * len(self.passed_levels)

	def end_exam(self, end="finish"):
		"""Show the summary of the exam, keep it in the history, say goodbye.

		end tells how it ended: "finish", "time" (time up) or "passed".
		"""
		elapsed = self.clock() - self.started_at
		self.console.print(display.summary_table(
			self.exam, self.passed_levels, self.attempts, self.oks, elapsed, self.grade,
		))
		if self.store:
			self.store.add_history(self._history_entry(end, elapsed))
			self.store.clear()
		self.console.print("End of the exam. See you soon!")

	def _history_entry(self, end, elapsed):
		"""What the history keeps of a finished exam: the base of a future score."""
		return {
			"exam": self.exam.id,
			"title": self.exam.title,
			"ended_at": datetime.fromtimestamp(self.clock()).isoformat(timespec="seconds"),
			"levels_passed": self.passed_levels,
			"grade": self.grade,
			"attempts": self.attempts,
			"oks": self.oks,
			"seconds": round(elapsed),
			"mode": self.mode,
			"end": end,
			**({"cheat": True} if self.cheated else {}),
		}

	def _save(self):
		"""Save the exam in progress, to resume it if the terminal is closed."""
		if self.store and self.variant:
			self.store.save(Session(
				self.exam.id, self.level, self.variant.id, self.started_at,
				self.mode, self.attempts, self.oks, self.failures,
				self.passed_levels, self.next_grademe_at, self.warned, self.cheated,
			))

	def _catalog(self):
		"""Return the catalog and the themes, loading them the first time."""
		if self.catalog is None:
			self.themes = self.themes or load_themes()
			self.catalog = load_catalog(themes=self.themes)
		return self.catalog, self.themes or load_themes()

	def _time_left(self):
		"""Seconds left before the end of the exam (0 or less: over; revision: no end)."""
		if self.mode == "revision":
			return math.inf
		return self.exam.duration_minutes * 60 - (self.clock() - self.started_at)

	def show_status(self):
		"""Show the exam, the level, the subject, the times and the next grademe."""
		elapsed = self.clock() - self.started_at
		left = max(0, self._time_left())
		if_ko = self.retry.wait_after(self.failures + 1)
		self.console.print(display.status_table(
			self.exam, self.level, self.variant, elapsed, left, self._wait_left(), if_ko,
			f"{RETRY_OF_MODE[self.mode]} ({', '.join(map(display.points, self.retry.minutes))} min)",
			self.grade, self.mode,
		))

	def _wait_left(self):
		"""Seconds left before the next grademe is allowed (0: now)."""
		if self.next_grademe_at is None:
			return 0
		return max(0, self.next_grademe_at - self.clock())

	def write_report(self):
		"""Write a report for an issue in reports/: the system, the subject, the code, the last trace.

		Return its path (kept in last_report).
		"""
		variant = self.variant
		subject = self.workspace.subjects / variant.name / "subject.en.txt"
		files = {}
		for name in variant.expected_files:
			path = self.workspace.rendu / variant.name / name
			files[name] = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None
		trace = None
		if self.last_trace and self.last_trace.name.endswith(f"_{variant.name}.trace") and self.last_trace.is_file():
			trace = self.last_trace.read_text(encoding="utf-8", errors="replace")
		text = full_report(f"{variant.id} ({variant.name})",
			subject.read_text(encoding="utf-8") if subject.is_file() else "", files, trace,
			variant.exercise.language, store=self.store)
		stamp = datetime.fromtimestamp(self.clock()).strftime("%Y%m%d-%H%M%S")
		self.workspace.reports.mkdir(parents=True, exist_ok=True)
		self.last_report = self.workspace.reports / f"{stamp}_{variant.name}.md"
		self.last_report.write_text(text, encoding="utf-8")
		self.console.print(display.report_written(self.last_report))
		return self.last_report

	def cheat(self):
		"""The cheat menu: the passphrase, then the menus of the pack; True if the exam is over.

		Back in a menu goes to the menu before; in the first one, back to the
		exam. A choice that opens no menu goes back to the exam too.
		"""
		menu = cheat.unlock(self.ask_password("Passphrase: "), self.cheat_pack)
		if menu is None:
			self.console.print("Wrong passphrase.")
			return False
		current, before = menu.first_menu(self), []
		while True:
			value = self._numbered_menu(current, first=not before)
			if value is BACK:
				if not before:
					return False
				current = before.pop()
				continue
			step = menu.choose(self, value)
			if step.text:
				self.console.print(step.text)
			if step.over or not step.menu:
				return step.over
			before.append(current)
			current = step.menu

	def _numbered_menu(self, menu, first):
		"""Show a menu (of the cheat menu, of the progress) as a numbered list; return the value picked, or BACK."""
		title, items = menu
		width = max(len(label) for _, label, _, _ in items) + 3
		lines = [title, *(f"  {number}. {label:{width}}{summary}"
			for number, (_, label, summary, _) in enumerate(items, start=1))]
		last = len(items) + 1
		lines.append(f"  {last}. {'Back to the exam' if first else 'Back (previous menu)'}")
		self._print_lines(lines)
		number = self._ask_choice("Your choice:", range(1, last + 1))
		self.console.print()
		return BACK if number == last else items[number - 1][0]

	def _ask_choice(self, prompt, allowed, default=None):
		"""Ask until the answer is one of the numbers of `allowed`; return it."""
		self.menus_shown += 1
		allowed = list(allowed)
		while True:
			answer = self.ask(prompt, default)
			if answer.isdigit() and int(answer) in allowed:
				return int(answer)
			choices = ", ".join(map(str, allowed))
			self.console.print(f"Invalid choice: type one of these numbers: {choices}.")

def complete_with(commands):
	"""Tab completes `commands` from now on, if readline is in use."""
	readline = sys.modules.get("readline")
	if readline is not None:
		readline.set_completer(make_completer(commands))

def terminal(commands):
	"""Prepare the real keyboard and terminal; return (console, ask, ask_password).

	readline gives input() the arrow keys (history, editing) and Tab to
	complete the `commands`.
	"""
	try:
		import readline
		readline.set_completer(make_completer(commands))
		# macOS ships libedit instead of GNU readline: another syntax.
		if "libedit" in (readline.__doc__ or ""):
			readline.parse_and_bind("bind ^I rl_complete")
		else:
			readline.parse_and_bind("tab: complete")
	except ImportError:
		pass

	def ask(prompt, default=None):
		"""Read a line; Enter alone gives `default`, shown in brackets."""
		shown = f"{prompt} [{default}] " if default else f"{prompt} "
		# The prompt goes to input() itself, not printed before by rich:
		# readline must know it, or Enter alone stays on the same line.
		answer = input(shown).strip()
		return answer if answer or default is None else default

	def ask_password(prompt):
		"""Read without showing what is typed, when the input is a terminal."""
		if sys.stdin.isatty():
			return getpass.getpass(prompt)
		# Answers sent through a pipe: getpass would wait on the keyboard.
		return input(prompt)

	return Console(), ask, ask_password

def main(full_screen=False, update_check=None):
	"""Start the examshell on the real keyboard and terminal; return the exit code.

	full_screen: the full-screen interface (pal42.cli.tui) instead of the text
	one. update_check: the check for a newer 42pal started at launch, if any.
	"""
	# rendu/ is a git repository that pushes to a bare one in ~/.42pal.
	workspace = Workspace(remote=STATE_DIR / "rendu.git")
	if full_screen:
		from pal42.cli.tui import run_exam
		return run_exam(workspace, SessionStore(), update_check)
	console, ask, ask_password = terminal(COMMANDS)
	try:
		shell = Shell(console, ask, ask_password, workspace=workspace, store=SessionStore())
		shell.update_check = update_check
		shell.run()
		if shell.restart:
			restart()
	except KeyboardInterrupt:
		console.print("\nExam stopped (Ctrl-C): run ./42pal again to resume it.")
		return 130
	return 0
