"""./42pal practice: subjects of one theme, one after the other.

No login, no exam timer, no wait between two grademe: a passed grademe
gives the next subject of the theme, and next skips to another one.
"""

import random
import time

from rich.markup import escape

from pal42.cli import display
from pal42.cli.shell import BACK, STATE_DIR, Shell, terminal
from pal42.session import SessionStore
from pal42.cli.workspace import Workspace
from pal42.practice import draw_practice

# The practice commands and what they do, shown by help.
PRACTICE_COMMANDS = {
	"grademe": "grade your work",
	"next": "another subject of the same theme",
	"report": "write a report for an issue: subject, your code, last trace",
	"finish": "stop practising",
	"help": "show this help",
}

# One letter (then Enter) for each command: g, n, r, f and ?.
PRACTICE_SHORTCUTS = {"g": "grademe", "n": "next", "r": "report", "f": "finish", "?": "help"}

class PracticeShell(Shell):
	"""Practising one theme: the grading and display of the examshell, no exam."""

	def __init__(self, console, ask, workspace=None, rng=None, catalog=None, themes=None,
			sleep=time.sleep, language=None, store=None):
		# store: where each grademe is kept for the progress (nothing is resumed).
		super().__init__(console, ask, None, workspace, rng or random.Random(),
			sleep=sleep, catalog=catalog, themes=themes, store=store)
		# None: asked in a menu when the catalog has more than one language.
		self.language = language
		self.theme = None
		# The subjects given so far (exo#seed), and how many were passed.
		self.seen = set()
		self.passed = 0

	def run(self, theme=None, first=True):
		"""Practise `theme` (asked if None); return the exit code.

		1 when the theme has no exercise (unknown, or none written yet).
		first: the menus of practice are the first ones shown, so their last
		choice quits; otherwise (practice chosen in the first menu of the
		examshell) it goes back, and run returns BACK.
		"""
		choices = self.practisable_themes()
		try:
			if theme is None:
				theme = self.choose_language_and_theme(first)
				if theme is None and not first:
					return BACK
				if theme is None:
					self.console.print("Goodbye!")
					return 0
			elif theme not in choices:
				self.console.print(
					f"No exercise to practise '{escape(theme)}' yet. Themes: {', '.join(choices)}"
				)
				return 1
			self.theme = theme
			self.next_subject()
		except EOFError:
			return 0
		self.command_loop()
		return 0

	def exercises_of(self, theme):
		"""The exercises of `theme`: a theme is the style of one real subject, in one language."""
		catalog, _ = self._catalog()
		return [exo for exo in catalog.exercises.values() if theme in exo.themes]

	def practisable_themes(self, language=None):
		"""The ids of the themes that have an exercise (in `language` if given), sorted."""
		_, themes = self._catalog()
		return sorted(theme for theme in themes if any(
			language in (None, exo.language) for exo in self.exercises_of(theme)))

	def practice_languages(self):
		"""The languages that have exercises, C first: {language: number of themes}."""
		catalog, _ = self._catalog()
		found = {exo.language for exo in catalog.exercises.values()}
		order = list(display.LANGUAGE_NAMES)
		languages = sorted(found, key=lambda language: order.index(language) if language in order else 99)
		return {language: len(self.practisable_themes(language)) for language in languages}

	def choose_language_and_theme(self, first=True):
		"""The language menu (when there are several), then the theme menu; None to leave.

		Back in the theme menu goes back to the language menu. first: the
		outer menu shown quits; otherwise it goes back (None too).
		"""
		languages = self.practice_languages()
		asks_language = self.language is None and len(languages) > 1
		while True:
			language = self.language
			if asks_language:
				language = self.choose_language(languages, first)
				if language is None:
					return None
			theme = self.choose_theme(self.practisable_themes(language), first=first and not asks_language)
			if theme is not None:
				return theme
			if not asks_language:
				return None

	def choose_language(self, languages, first=True):
		"""Show the languages as a numbered menu; return the one picked, or None to leave."""
		self.console.print("Choose a language:")
		for number, (language, count) in enumerate(languages.items(), start=1):
			name = display.LANGUAGE_NAMES.get(language, language)
			self.console.print(f"  {number}. {name} ({count} theme{'s' if count != 1 else ''})")
		last = len(languages) + 1
		self.console.print(display.last_choice(last, first=first), markup=False)
		number = self._ask_choice("Your choice:", range(1, last + 1))
		self.console.print()
		return None if number == last else list(languages)[number - 1]

	def choose_theme(self, choices, first=True):
		"""Show the themes as a numbered menu, with their skill; return the one picked.

		The last choice quits (first menu) or goes back: None is returned.
		"""
		_, themes = self._catalog()
		self.console.print("Choose a theme to practise:")
		for number, theme in enumerate(choices, start=1):
			self.console.print(f"  {number}. {theme} · {escape(themes[theme].skill)}")
		last = len(choices) + 1
		self.console.print(display.last_choice(last, first=first), markup=False)
		number = self._ask_choice("Your choice:", range(1, last + 1))
		if not first and number == last:
			self.console.print()
		return None if number == last else choices[number - 1]

	def next_subject(self):
		"""Give a new subject of the theme, one not given before."""
		self.variant = draw_practice(self.exercises_of(self.theme), self.rng, self.seen)
		self.seen.add(self.variant.id)
		self.show_subject()

	def show_subject(self):
		"""Write the current subject in the workspace and show it."""
		_, themes = self._catalog()
		subject = self.workspace.give_subject(self.variant)
		rendu = self.workspace.rendu / self.variant.name
		self.console.print()
		self.console.print(display.practice_panel(
			themes[self.theme], self.variant, subject, rendu,
		))
		self.console.print()
		# The words of the variant stand out; rich reads no markup in a Text.
		self.console.print(display.subject_text(self.variant, subject.read_text(encoding="utf-8")), end="")
		self.console.print()

	def command_loop(self):
		"""Read and run the practice commands until finish or Ctrl-D."""
		while True:
			try:
				command = self.ask("practice>").strip()
			except EOFError:
				command = "finish"
			if self.handle(command):
				return

	def handle(self, command):
		"""Run one practice command; return True when the practice is over."""
		command = PRACTICE_SHORTCUTS.get(command.strip(), command.strip())
		if command == "finish":
			self.console.print(
				f"Practice summary: {self.passed} subject{'s' if self.passed != 1 else ''}"
				f" passed, {self.attempts} grademe"
			)
			return True
		if command == "help":
			self.console.print(display.help_table(PRACTICE_COMMANDS))
		elif command == "next":
			self.next_subject()
		elif command == "report":
			self.write_report()
		elif command == "grademe":
			# None: the default command of the language (cc -Wall -Wextra -Werror, python3).
			if self._grade_and_show(None).passed:
				self.passed += 1
				self.next_subject()
		elif command:
			self.console.print(f"Unknown command: {escape(command)}. Type help for the list.")
		if command:
			self.console.print()
		return False

def main(theme=None, full_screen=False):
	"""Practise on the real keyboard and terminal; return the exit code.

	full_screen: the full-screen interface (pal42.cli.tui) instead of the text one.
	"""
	workspace = Workspace(remote=STATE_DIR / "rendu.git")
	if full_screen:
		from pal42.cli.tui import run_practice
		return run_practice(workspace, theme)
	console, ask, _ = terminal(PRACTICE_COMMANDS)
	try:
		return PracticeShell(console, ask, workspace, store=SessionStore()).run(theme)
	except KeyboardInterrupt:
		console.print("\nPractice stopped (Ctrl-C).")
		return 130
