"""How the examshell looks: the rich panels and tables it prints.

Each function returns something rich can print; the shell prints it.
"""

import re
import time
from datetime import datetime, timedelta
from pathlib import Path

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

def short_path(path):
	"""Write `path` with ~ for the home folder, like a shell does."""
	path = Path(path)
	home = Path.home()
	if path == home or home in path.parents:
		return "~/" + path.relative_to(home).as_posix()
	return path.as_posix()

def path_link(path, end=""):
	"""A path the terminal opens when it is clicked: [link=file://...]~/path[/link]."""
	return f"[link={Path(path).resolve().as_uri()}]{escape(short_path(path))}{end}[/link]"

# How the words of a variant stand out in its subject, on the screen.
VARIANT_STYLE = "bold #c4b5fd"

def subject_text(variant, text):
	"""The subject as a rich Text, the texts of the params of `variant` in VARIANT_STYLE.

	What changes from a variant to another stands out; the file of the
	subject stays plain text. Only the statement is looked at (between the
	line of dashes and the examples); a text cut by the wrapping is found
	all the same.
	"""
	styled = Text(text)
	start = max(0, text.find("-" * 80))
	end = text.find("\nExamples:")
	end = len(text) if end < 0 else end
	for param in variant.exercise.params:
		words = param.text(variant.params[param.name]).split()
		if not words:
			continue
		pattern = r"\s+".join(map(re.escape, words))
		# A short text, like 5, only as a whole word.
		if words[0][0].isalnum():
			pattern = r"\b" + pattern
		if words[-1][-1].isalnum():
			pattern += r"\b"
		for match in re.compile(pattern).finditer(text, start, end):
			styled.stylize(VARIANT_STYLE, match.start(), match.end())
	return styled

def subject_panel(exam, level, variant, subject, rendu, mode="exam"):
	"""The panel shown when a subject is given; mode is "exam" or "revision"."""
	if mode == "revision":
		how = "revision mode · soft waits · no time limit"
	else:
		how = f"exam mode · hard waits · {exam.duration_minutes} min"
	# escape: a [ in a path would otherwise be read as rich markup.
	lines = [
		f"[bold]{escape(exam.title)}[/] · level {level} · {how}",
		f"This level is worth {points(exam.points_per_level)} points.",
		"",
		f"Subject: [bold cyan]{escape(variant.name)}[/]",
		f"Read it: {path_link(subject)}",
		f"Hand in: {path_link(rendu, '/')}",
	]
	# 80 wide, like the subject printed under it (narrower if the terminal is).
	return Panel("\n".join(lines), title="42pal", width=80)

def duration(seconds):
	"""Write a number of seconds as H:MM:SS, like 0:10:00."""
	return str(timedelta(seconds=int(seconds)))

def report_written(path):
	"""Said after the report command: where the report is, and what to do with it."""
	return (f"Report written: {path_link(path)}\n"
		"Attach it to an issue on GitHub (Issues, then New issue), or paste it there."
		" It holds your code: share it only if you want to.")

def help_table(commands):
	"""The table of the examshell commands, from {command: what it does}."""
	table = Table(title="Commands", show_header=False, box=None,
		caption="Something wrong? Run ./42pal --report and open an issue on GitHub.")
	for command, meaning in commands.items():
		table.add_row(f"[bold]{command}[/]", meaning)
	return table

def status_table(exam, level, variant, elapsed, left, wait=0, if_ko=0, retry="", grade=0,
		mode="exam"):
	"""Where the student is: exam, level, subject, times, and the next grademe.

	wait is the time left before grademe is allowed again; if_ko the wait
	that a failed grademe would bring; retry describes the retry timer.
	"""
	table = Table(show_header=False, box=None)
	table.add_row("Exam", escape(exam.title))
	table.add_row("Mode", mode)
	table.add_row("Level", f"{level} of {exam.level_count}")
	table.add_row("Subject", f"[bold cyan]{escape(variant.name)}[/]")
	table.add_row("Grade", f"{points(grade)}/100")
	table.add_row("Time spent", duration(elapsed))
	table.add_row("Time left", "no limit" if left == float("inf") else duration(left))
	table.add_row("Next grademe", f"in {duration(wait)}" if wait else "now")
	table.add_row("If KO", duration(if_ko) if if_ko else "no wait")
	if retry:
		table.add_row("Retry timer", retry)
	return table

def retry_preview(wait):
	"""Said before grading: the wait a KO would bring."""
	when = f"in {duration(wait)}" if wait else "right away"
	return f"[dim]If KO: next grademe {when}[/]"

def next_grademe(wait, next_wait):
	"""Said after a KO: when grademe is allowed again, and what the next KO costs."""
	if wait:
		at = (datetime.now() + timedelta(seconds=wait)).strftime("%H:%M")
		when = f"in {duration(wait)} (at {at})"
	else:
		when = "now (the first retry is free)"
	again = duration(next_wait) if next_wait else "no wait"
	return f"[yellow]Next grademe {when}[/] · if KO again: {again}"

def wait_message(wait):
	"""Said when grademe comes before the end of the wait."""
	return f"[yellow]Wait {duration(wait)} before your next grademe.[/]"

def typewriter(console, text, sleep=time.sleep, delay=0.02):
	"""Print `text` one letter at a time, as if someone were typing it.

	Only in a real terminal: in a pipe or a test, it is printed at once.
	sleep is given by the tests, so that they do not wait.
	"""
	if not console.is_terminal:
		console.print(text, markup=False, highlight=False)
		return
	for char in text:
		console.print(char, end="", markup=False, highlight=False)
		# Without flush, the terminal would show the line only once complete.
		console.file.flush()
		sleep(delay)
	console.print()

# A trace longer than this is cut on screen; the whole of it is in its file.
TRACE_LINES_SHOWN = 25

def grade_result(grade, log):
	"""The result of a grademe: OK or KO, the tests passed, the clickable log."""
	if grade.passed:
		verdict = f"[bold green]✓ OK[/]  {grade.tests_passed}/{grade.tests_total} tests"
	else:
		verdict = f"[bold red]✗ KO[/]  {grade.tests_passed}/{grade.tests_total} tests passed"
	# [link=...]: the terminal opens the file when the path is clicked.
	link = path_link(log)
	warnings = "".join(f"\n[yellow]! {escape(warning)}[/]" for warning in grade.warnings)
	return f"{verdict}\nTrace: {link}{warnings}"

def trace_panel(trace):
	"""The trace in a red frame, cut after TRACE_LINES_SHOWN lines."""
	lines = trace.rstrip("\n").splitlines()
	shown = "\n".join(lines[:TRACE_LINES_SHOWN])
	# Text: the trace is shown as it is, with no rich markup read in it.
	text = Text(shown)
	if len(lines) > TRACE_LINES_SHOWN:
		more = len(lines) - TRACE_LINES_SHOWN
		text.append(f"\n… {more} more lines: see the trace file", style="dim")
	# 84 wide: the 80 columns of a trace line, plus the frame and its margins.
	return Panel(text, title="trace", border_style="red", width=84)

def exam_passed_panel(exam):
	"""The panel shown when the last playable level is passed."""
	return Panel(
		f"[bold green]Well done! Exam passed[/]: {escape(exam.title)}, grade 100/100.",
		border_style="green", width=80,
	)

def time_up():
	"""Said when a command comes after the end of the exam."""
	return "[bold red]Time is up![/] The exam is over: no more grademe."

def almost_over(left):
	"""Said once, when less than 10 minutes are left."""
	return f"[bold yellow]Less than 10 minutes left[/] ({duration(left)})."

def summary_table(exam, passed_levels, attempts, oks, elapsed, grade=0):
	"""The summary at the end of the exam: grade, levels passed, grademe, time spent."""
	table = Table(title=f"Summary · {escape(exam.title)}", show_header=False, box=None)
	levels = ", ".join(map(str, passed_levels)) or "none"
	table.add_row("Grade", f"{points(grade)}/100")
	table.add_row("Levels passed", f"{len(passed_levels)} ({levels})")
	table.add_row("Grademe", f"{attempts} ({oks} OK, {attempts - oks} KO)")
	table.add_row("Time spent", duration(elapsed))
	return table

def resume_question(exam, level, variant, left):
	"""The question asked when a saved exam can be resumed."""
	time = "no time limit" if left == float("inf") else f"{duration(left)} left"
	return f"Resume your exam? {exam.title} · level {level} · {variant.name} · {time} (y/n)"

def time_ran_out_while_away(exam):
	"""Said when the saved exam ended while the terminal was closed."""
	return (f"[yellow]Your last exam ({escape(exam.title)}) time ran out while you were"
		" away: it is kept in your history.[/]")

def cannot_resume(variant_id):
	"""Said when the subject of the saved exam no longer exists."""
	return f"[yellow]Your last exam cannot be resumed: its subject {escape(variant_id)} is gone.[/]"

def practice_panel(theme, variant, subject, rendu):
	"""The panel shown when a practice subject is given."""
	lines = [
		f"[bold]Practice · {escape(theme.id)}[/] · {escape(theme.skill)}",
		"No timer, no wait: grademe, next, finish",
		"",
		f"Subject: [bold cyan]{escape(variant.name)}[/]",
		f"Read it: {path_link(subject)}",
		f"Hand in: {path_link(rendu, '/')}",
	]
	return Panel("\n".join(lines), title="42pal", width=80)

def update_message(update):
	"""Said when a newer 42pal is found: how many commits, and the last ones."""
	plural = "s" if update.count != 1 else ""
	lines = [f"[bold #a5b4fc]A new version of 42pal is available: {update.count} new commit{plural}.[/]"]
	lines += [f"  · {escape(change)}" for change in update.changes]
	return "\n".join(lines)

def update_failed(why):
	"""Said when git pull refused: nothing was changed."""
	return f"[yellow]The update failed: {escape(why)}[/] Nothing was changed; 42pal goes on."

def points(value):
	"""Write points with 2 decimals at most and no useless zero: 25, 12.5, 16.67."""
	return f"{round(value, 2):g}"

# The menus before the exam. Their lines stay under 80 characters.

# How the first menu names each audience (see AUDIENCES in pal42/exam.py).
AUDIENCE_TEXTS = {"piscine": "Piscine (piscineux)", "student": "Student (cursus)"}

def exam_length(minutes):
	"""Write a duration for a menu: 3 h, 4 h 30, or 45 min."""
	hours, rest = divmod(minutes, 60)
	if not hours:
		return f"{rest} min"
	return f"{hours} h {rest:02d}" if rest else f"{hours} h"

# How a menu names the language of an exam.
LANGUAGE_NAMES = {"c": "C", "cpp": "C++", "python": "Python"}

def exam_summary(exam):
	"""The size and language of an exam, for a menu: 8 levels, 4 h, C."""
	return (f"{exam.level_count} levels, {exam_length(exam.duration_minutes)}, "
		f"{LANGUAGE_NAMES.get(exam.language, exam.language)}")

def exam_tools(exam):
	"""How the rendus of an exam are built: compiled in C, run in Python."""
	verb = "Run" if exam.language == "python" else "Compiled"
	return f"{verb} with {' '.join(exam.compile_command)}."

def last_choice(number, first):
	"""The last choice of a menu: back to the menu before, or quit in the first one."""
	return f"  {number}. {'Quit' if first else 'Back (previous menu)'}"

# The first menu: its title, and the choice that leads to practice.
FIRST_MENU_TITLE = "What do you want to do?"
PRACTICE_TEXT = "Practice"
PRACTICE_SUMMARY = "one theme, no timer"

# The choice of the first menu that shows the progress.
PROGRESS_TEXT = "Progress"
PROGRESS_SUMMARY = "your exams and weak themes"

def audience_menu(exams_by_audience, first=True, practice=False, progress=False):
	"""The first menu: the exams of the piscine or of the students, then practice and progress."""
	lines = [FIRST_MENU_TITLE]
	for number, (audience, exams) in enumerate(exams_by_audience.items(), start=1):
		leads_to = exams[0].title if len(exams) == 1 else f"{len(exams)} exams"
		lines.append(f"  {number}. {AUDIENCE_TEXTS[audience]:22}{leads_to}")
	count = len(exams_by_audience)
	if practice:
		count += 1
		lines.append(f"  {count}. {PRACTICE_TEXT:22}{PRACTICE_SUMMARY}")
	if progress:
		count += 1
		lines.append(f"  {count}. {PROGRESS_TEXT:22}{PROGRESS_SUMMARY}")
	return lines + [last_choice(count + 1, first)]

def progress_summary(text):
	"""The first line of the progress."""
	return f"[bold]Progress[/] · {escape(text)}"

def exam_progress_table(rows):
	"""The exams taken: how many times, passed, and the best grade."""
	table = Table(show_header=True, box=None, header_style="dim")
	for column in ("Exam", "Taken", "Passed", "Best"):
		table.add_column(column)
	for row in rows:
		table.add_row(escape(row.title), str(row.tries), str(row.passed), f"{points(row.best)}/100")
	return table

def theme_score(row):
	"""How a theme went: 1 OK out of 3 grademe."""
	return f"{row.oks} OK out of {row.tries} grademe"

def exam_menu(exams, first=False):
	"""The menu of the exams: each title with its levels and duration."""
	width = max(len(exam.title) for exam in exams) + 3
	lines = ["Choose your exam:"]
	for number, exam in enumerate(exams, start=1):
		lines.append(f"  {number}. {exam.title:{width}}{exam_summary(exam)}")
	return lines + [last_choice(len(exams) + 1, first)]

def mode_menu(exam, first=False):
	"""The menu of the modes: what each one means for the time and the waits."""
	hard = ", ".join(map(points, exam.retry["hard"].minutes))
	soft = ", ".join(map(points, exam.retry["soft"].minutes))
	indent = " " * 15
	return [
		"Choose the mode:",
		f"  1. Exam      The real conditions: {exam_length(exam.duration_minutes)}, "
			"then the exam ends.",
		f"{indent}Waits after a failed grademe grow fast (minutes):",
		f"{indent}{hard}",
		"  2. Revision  No time limit.",
		f"{indent}Waits after a failed grademe stay short (minutes):",
		f"{indent}{soft}",
		last_choice(3, first),
		"Enter alone takes revision.",
	]

def level_menu(exam, first=False):
	"""What the starting level means: the points of a level, the levels skipped.

	Its last choice comes after the last level: 5 for an exam of 4 levels.
	"""
	playable = ", ".join(map(str, exam.playable_levels))
	return [
		"Choose the starting level:",
		f"  {exam.level_count} levels, worth {points(exam.points_per_level)} points each: "
			"pass them all for 100/100.",
		"  If you start higher, the levels before it give no points.",
		f"  Levels you can play: {playable}.",
		last_choice(exam.level_count + 1, first),
	]

def points_won(won, grade):
	"""Said after an OK: the points of the level, and the grade now."""
	return f"[bold green]+{points(won)} points[/] · grade {points(grade)}/100"

def no_more_levels(grade):
	"""Said when the last playable level is passed but the grade is below 100."""
	return (f"[yellow]No more playable level for now: your grade is {points(grade)}/100.[/]"
		" The next levels have no exercise yet.")
