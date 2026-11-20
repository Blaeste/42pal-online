"""The full-screen interface of 42pal, built with textual (copied into vendor/).

The shells of the text interface do all the work (pal42.cli.shell and
pal42.cli.practice): this module shows their menus as screens, sends them
the commands typed, and shows what they print. Its look is in tui.tcss.

The flow: a fake login, the saved exam to resume if any, then the menus
(who, which exam, which mode, which level), each with a last choice to go
back; then the session screen, until the exam ends.
"""

import asyncio
import getpass
import io
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlparse

from rich.console import Console
from rich.markup import escape
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.css.scalar import ScalarOffset
from textual.screen import Screen
from textual.strip import Strip
from textual.suggester import SuggestFromList
from textual.widgets import Input, OptionList, RichLog, Static
from textual.widgets.option_list import Option

from pal42 import cheat
from pal42.cli import display
from pal42.cli.practice import PRACTICE_COMMANDS, PRACTICE_SHORTCUTS, PracticeShell
from pal42.cli.shell import BACK, COMMANDS, PRACTICE, PROGRESS, SHORTCUTS, Shell
from pal42.exam import AUDIENCES
from pal42.progress import exam_rows, summary, weak_themes
from pal42.session import SessionStore
from pal42.update import apply_update, restart

LOGO = [
	"██╗  ██╗██████╗ ██████╗  █████╗ ██╗     ",
	"██║  ██║╚════██╗██╔══██╗██╔══██╗██║     ",
	"███████║ █████╔╝██████╔╝███████║██║     ",
	"╚════██║██╔═══╝ ██╔═══╝ ██╔══██║██║     ",
	"     ██║███████╗██║     ██║  ██║███████╗",
	"     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝",
]

# The colors the logo goes through, cyan to violet; they move slowly.
GRADIENT = ["#5eead4", "#67e8f9", "#7dd3fc", "#93c5fd", "#a5b4fc", "#c4b5fd", "#d8b4fe"]

TAGLINE = "exam trainer · random variants · local moulinette"

# What the app exits with once a newer 42pal is pulled: it must start again.
RESTART = object()

# Under this many lines, the screens get the "-compact" class (see tui.tcss).
COMPACT_HEIGHT = 30

# From this many columns, the subject and the log stand side by side.
WIDE_WIDTH = 150

def hints(pairs):
	"""The line of keys at the bottom of a screen: [("⏎", "choose"), ...]."""
	text = Text()
	for key, what in pairs:
		if text:
			text.append("   ")
		text.append(key, style="bold #a5b4fc")
		text.append(f" {what}")
	return text

def option_label(title, meta):
	"""A menu choice: its title in bold, a grey line under it."""
	label = Text(title, style="bold")
	if meta:
		label.append(f"\n{meta}", style="dim")
	return label

# A web address in a text: up to a space, a quote or a closing bracket.
WEB_ADDRESS = re.compile(r"https?://[^\s'\")\]>]+")

def open_on_click(target):
	"""The style of a text that opens `target` (a path or a web address) when clicked."""
	return Style(underline=True, meta={"@click": f"app.open_link({target!r})"})

def link_target(link):
	"""What to open for a rich link: the path of a file:// link, or the address."""
	parts = urlparse(link)
	return unquote(parts.path) if parts.scheme == "file" else link

def clickable(text):
	"""Make the links of `text` open with a click: rich links and web addresses.

	Textual does not open the links of rich (the terminal would, but textual
	keeps the mouse): each one gets a click action instead (see open_link).
	"""
	for span in list(text.spans):
		style = Style.parse(span.style) if isinstance(span.style, str) else span.style
		if style.link:
			text.stylize(open_on_click(link_target(style.link)), span.start, span.end)
	for match in WEB_ADDRESS.finditer(text.plain):
		text.stylize(open_on_click(match.group()), match.start(), match.end())
	return text

def launch(command):
	"""Start `command` apart from 42pal: it goes on if 42pal stops, and says nothing."""
	subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL, start_new_session=True)

# The programs that put a text in the clipboard, the first one found is used:
# many terminals (GNOME Terminal among them) ignore the clipboard sequence
# that textual sends.
CLIPBOARD_COMMANDS = [
	["wl-copy"],
	["xclip", "-selection", "clipboard"],
	["xsel", "--clipboard", "--input"],
	["pbcopy"],
]

def capture_console():
	"""The console the shells print to: kept as text with colors, for the screens."""
	return Console(file=io.StringIO(), force_terminal=True, color_system="truecolor", width=100)

class Logo(Static):
	"""The 42pal logo; its gradient moves slowly. One line on a small terminal."""

	def on_mount(self):
		self.shift = 0
		self.paint()
		self.set_interval(0.12, self.paint)

	def paint(self):
		self.shift += 1
		lines = ["4 2 p a l"] if self.screen.has_class("-compact") else LOGO
		text = Text()
		for row, line in enumerate(lines):
			for col, char in enumerate(line):
				text.append(char, style=GRADIENT[((col + row * 2 - self.shift) // 4) % len(GRADIENT)])
			if row < len(lines) - 1:
				text.append("\n")
		self.update(text)

class IntroScreen(Screen):
	"""A screen with the logo and a card: they come in with a short animation."""

	def on_resize(self, event):
		self.set_class(event.size.height < COMPACT_HEIGHT, "-compact")

	def animate_in(self):
		"""The logo drops in, the card rises, the texts appear one after the other.

		Not when the animations are off (TEXTUAL_ANIMATIONS=none, or the tests).
		"""
		if self.app.animation_level == "none":
			return
		logo = self.query_one(".logo")
		logo.styles.offset = (0, -4)
		logo.styles.opacity = 0.0
		logo.styles.animate("offset", ScalarOffset.from_offset((0, 0)), duration=0.6, easing="out_back")
		logo.styles.animate("opacity", 1.0, duration=0.5)
		# The card rises from below; no fading: the opacity would break its background.
		card = self.query_one(".card")
		card.styles.offset = (0, 3)
		card.styles.animate("offset", ScalarOffset.from_offset((0, 0)), duration=0.5,
			easing="out_cubic", delay=0.15)
		for delay, widget in zip((0.15, 0.45, 0.6), self.query(".tagline, .details, .hints")):
			widget.styles.opacity = 0.0
			self.set_timer(delay, lambda w=widget: w.styles.animate("opacity", 1.0, duration=0.4))

class LoginScreen(IntroScreen):
	"""The fake login, like at the exam: any password, never checked nor kept.

	It is dismissed with the login typed (the user name by default).
	"""

	BINDINGS = [("escape", "app.quit", "Quit")]

	def __init__(self, user):
		super().__init__()
		self.user = user

	def compose(self) -> ComposeResult:
		with Vertical(classes="root"):
			yield Static(classes="logo")
			yield Static("examshell", classes="tagline")
			with Vertical(classes="card"):
				yield Static("login", classes="field-label")
				yield Input(value=self.user, id="login")
				yield Static("password", classes="field-label")
				yield Input(password=True, id="password")
			yield Static(hints([("⏎", "next"), ("esc", "quit")]), classes="hints")

	def on_mount(self):
		# A Logo widget for the logo: the placeholder was only for the layout.
		self.query_one(".logo").remove()
		self.query_one(".root").mount(Logo(classes="logo"), before=0)
		self.query_one(".card").border_title = " Log in "
		self.query_one("#login", Input).focus()
		self.call_after_refresh(self.animate_in)

	def on_input_submitted(self, event):
		if event.input.id == "login":
			self.query_one("#password", Input).focus()
			return
		# The password is dropped at once: not checked, not stored.
		event.input.value = ""
		self.dismiss(self.query_one("#login", Input).value.strip() or self.user)

class PassphraseScreen(Screen):
	"""The passphrase of the cheat menu, hidden as it is typed; dismissed with it ("" for Esc)."""

	BINDINGS = [("escape", "cancel", "Back")]

	def compose(self) -> ComposeResult:
		with Vertical(classes="root"):
			with Vertical(classes="card"):
				yield Static("passphrase", classes="field-label")
				yield Input(password=True, id="passphrase")
			yield Static(hints([("⏎", "unlock"), ("esc", "back")]), classes="hints")

	def on_mount(self):
		self.query_one(".card").border_title = " Cheat "
		self.query_one("#passphrase", Input).focus()

	def on_input_submitted(self, event):
		passphrase = event.value
		event.input.value = ""
		self.dismiss(passphrase)

	def action_cancel(self):
		self.dismiss("")

class MenuScreen(IntroScreen):
	"""A menu: a choice per item, then Back (or Quit in the first menu).

	items are (value, title, meta, details): meta is the grey line under the
	title, details the text shown under the card while the item is
	highlighted. The screen is dismissed with the value of the item chosen,
	or BACK.
	"""

	BINDINGS = [
		("escape", "back", "Back"),
		("q", "app.quit", "Quit"),
		("j", "move(1)", "Down"),
		("k", "move(-1)", "Up"),
	]

	def __init__(self, title, items, first, highlight=0, last=None, subtitle=TAGLINE):
		super().__init__()
		self.title = title
		self.subtitle = subtitle
		self.items = list(items)
		self.first = first
		self.highlight = highlight
		# last: (label, details) of the last choice, instead of Quit or Back.
		self.last_label, self.last_details = last or (
			("Quit", "Quit 42pal.") if first else ("Back", "Back to the menu before."))

	def compose(self) -> ComposeResult:
		with Vertical(classes="root"):
			yield Logo(classes="logo")
			yield Static(self.subtitle, classes="tagline")
			with Vertical(classes="card"):
				options = [Option(option_label(title, meta), id=str(index))
					for index, (_, title, meta, _) in enumerate(self.items)]
				options.append(None)
				options.append(Option(Text(self.last_label, style="dim"), id="back"))
				yield OptionList(*options)
			yield Static(classes="details")
			# Esc chooses the last choice: it quits only when that choice is Quit.
			yield Static(hints([("↑↓ jk", "move"), ("⏎", "choose"),
				("esc", "quit" if self.last_label == "Quit" else "back"), ("q", "quit")]), classes="hints")

	def on_mount(self):
		self.query_one(".card").border_title = f" {self.title} "
		menu = self.query_one(OptionList)
		menu.highlighted = self.highlight
		menu.focus()
		self.call_after_refresh(self.animate_in)

	def action_move(self, step):
		menu = self.query_one(OptionList)
		menu.action_cursor_down() if step > 0 else menu.action_cursor_up()

	def action_back(self):
		self.dismiss(BACK)

	def on_option_list_option_highlighted(self, event):
		details = self.query_one(".details", Static)
		if event.option.id == "back":
			details.update(self.last_details)
		else:
			details.update(self.items[int(event.option.id)][3])
		details.styles.opacity = 0.3
		details.styles.animate("opacity", 1.0, duration=0.25)

	def on_option_list_option_selected(self, event):
		if event.option.id == "back":
			self.dismiss(BACK)
		else:
			self.dismiss(self.items[int(event.option.id)][0])

class Activity:
	"""The spinner of a grading, for the session screen: update(text) shows a text.

	`show` is called with the text, then with None at the end; the shells
	use it from the thread that grades.
	"""

	def __init__(self, show, text):
		self.show = show
		self.text = text

	def __enter__(self):
		self.show(self.text)
		return self

	def update(self, text):
		self.show(text)

	def __exit__(self, *error):
		self.show(None)

class SelectableLog(RichLog):
	"""The log of a session, whose text can be selected with the mouse.

	RichLog keeps its lines already drawn, with their colors: the selection
	is taken from their text, and drawn over them.
	"""

	def get_selection(self, selection):
		text = "\n".join(line.text.rstrip() for line in self.lines)
		return selection.extract(text), "\n"

	def selection_updated(self, selection):
		self.refresh()

	def render_line(self, y):
		strip = super().render_line(y)
		line = self.scroll_offset.y + y
		if line >= len(self.lines):
			return strip
		# Where the line is in the text: textual needs it to know what the mouse selects.
		strip = strip.apply_offsets(self.scroll_offset.x, line)
		selection = self.text_selection
		span = selection.get_span(line) if selection is not None else None
		if span is None:
			return strip
		start, end = span
		if end == -1:
			end = len(self.lines[line].text.rstrip())
		start = max(0, start - self.scroll_offset.x)
		end = min(strip.cell_length, end - self.scroll_offset.x)
		if start >= end:
			return strip
		before, selected, after = strip.divide([start, end, strip.cell_length])
		# Only the background of the selection, over each piece: its own
		# background would hide it below, and its text keeps its color.
		style = Style(bgcolor=self.screen.get_component_rich_style("screen--selection").bgcolor)
		selected = Strip([Segment(piece, (piece_style or Style()) + style, control)
			for piece, piece_style, control in selected], selected.cell_length)
		return Strip.join([before, selected, after])

class ScreenShellMixin:
	"""What the shells change on a screen: the subject goes to its own pane.

	activity is set by the session screen: a function that shows the text of
	the spinner while grading, or hides it with None.
	"""

	activity = None

	def show_subject(self):
		# Only written: the session screen shows it in its pane.
		self.workspace.give_subject(self.variant)

	def _status(self, text):
		return Activity(self.activity or (lambda text: None), text)

class ScreenShell(ScreenShellMixin, Shell):
	"""The examshell, for the full-screen interface."""

class ScreenPracticeShell(ScreenShellMixin, PracticeShell):
	"""The practice shell, for the full-screen interface."""

class SessionScreen(Screen):
	"""An exam (or a practice): the header, the subject, the log, the command line.

	The commands are typed like in the examshell; the shell runs them and
	what it prints goes to the log. A grading runs in a thread, so that the
	screen stays alive. When the exam is over, Enter leaves; the screen is
	dismissed with the last thing printed (the summary). PgUp and PgDn
	scroll the subject while typing; up and down bring back the commands
	typed before, like in a shell.
	"""

	BINDINGS = [
		("pageup", "scroll_subject(-1)", "Subject up"),
		("pagedown", "scroll_subject(1)", "Subject down"),
		("up", "history(-1)", "Previous command"),
		("down", "history(1)", "Next command"),
		# Copies the selection like Ctrl+C, in the terminals that let it through;
		# with nothing selected, it does nothing (Ctrl+C would leave).
		("ctrl+shift+c", "screen.copy_text", "Copy"),
	]

	def __init__(self, shell, practice=False):
		super().__init__()
		self.shell = shell
		self.practice = practice
		self.commands = PRACTICE_COMMANDS if practice else COMMANDS
		self.shortcuts = PRACTICE_SHORTCUTS if practice else SHORTCUTS
		self.prompt = "practice>" if practice else "examshell>"
		self.shown_variant = None
		self.busy = False
		self.over = False
		self.final = ""
		# The commands typed, the oldest first; while going through them, the
		# place shown (None: not going through) and what was being typed.
		self.history = []
		self.history_place = None
		self.draft = ""

	def compose(self) -> ComposeResult:
		yield Static(id="header")
		with Container(id="body"):
			with VerticalScroll(id="subject-pane"):
				yield Static(id="subject")
			# No wrap: the shell already prints at the width of the log (see
			# fit_console); wrapping again would cut the frames at their spaces.
			yield SelectableLog(id="log", wrap=False, markup=False, highlight=False)
		yield Static(id="activity")
		letters = ", ".join(f"{letter} {command}" for letter, command in self.shortcuts.items())
		yield Input(id="command", placeholder=f"{self.prompt} type a command ({letters})",
			suggester=SuggestFromList(list(self.commands), case_sensitive=False))
		# The one-letter commands are in the placeholder of the command line.
		yield Static(hints([("↑↓", "history"), ("→", "complete"), ("pgup pgdn", "subject"),
			("ctrl+c ctrl+shift+c", "copy"), ("r", "report"), ("ctrl+q", "leave")]), id="session-hints")

	def on_mount(self):
		self.query_one("#log").border_title = " log "
		# The shell shows the spinner of a grading on this screen.
		self.shell.activity = lambda text: self.app.call_from_thread(self.show_activity, text)
		self.refresh_subject()
		self.refresh_header()
		self.set_interval(1, self.tick)
		self.query_one("#command", Input).focus()

	def on_resize(self, event):
		self.set_class(event.size.width >= WIDE_WIDTH, "-wide")

	def action_history(self, step):
		"""Up (-1) and down (1): the commands typed before; below the last, the draft."""
		if not self.history or self.busy or self.over:
			return
		command = self.query_one("#command", Input)
		if self.history_place is None:
			if step > 0:
				return
			self.draft = command.value
			self.history_place = len(self.history)
		self.history_place = max(0, self.history_place + step)
		if self.history_place >= len(self.history):
			self.history_place = None
			value = self.draft
		else:
			value = self.history[self.history_place]
		command.value = value
		command.cursor_position = len(value)

	def action_scroll_subject(self, step):
		pane = self.query_one("#subject-pane")
		pane.scroll_page_down() if step > 0 else pane.scroll_page_up()

	def fit_console(self):
		"""What the shell prints is as wide as the log."""
		width = self.query_one("#log").scrollable_content_region.width
		self.shell.console.width = max(40, width - 1)

	def refresh_subject(self):
		"""Show the current subject in its pane, when it is a new one."""
		variant = self.shell.variant
		if variant is None or variant.id == self.shown_variant:
			return
		self.shown_variant = variant.id
		workspace = self.shell.workspace
		subject = workspace.subjects / variant.name / "subject.en.txt"
		rendu = workspace.rendu / variant.name
		# The paths open with a click: the subject in an editor, the rendu in
		# the file manager. One Text: textual can only select in a single text,
		# for the prototypes and headers to be copied.
		content = Text()
		content.append("Read it  ", style="dim")
		content.append(display.short_path(subject), style=open_on_click(str(subject)))
		content.append("\nHand in  ", style="dim")
		content.append(f"{display.short_path(rendu)}/", style=open_on_click(str(rendu)))
		content.append("\n\n")
		# The words of the variant stand out (see display.subject_text).
		content.append_text(display.subject_text(variant, subject.read_text(encoding="utf-8")))
		self.query_one("#subject", Static).update(content)
		pane = self.query_one("#subject-pane")
		pane.border_title = f" {variant.name} "
		pane.scroll_home(animate=False)

	def refresh_header(self):
		"""The exam, the level, the time and the grade, or how the practice goes."""
		shell = self.shell
		header = self.query_one("#header", Static)
		text = Text()
		if self.practice:
			header.border_title = " 42pal · practice "
			text.append(shell.theme, style="bold #e0e7ff")
			text.append(f"   {shell.passed} passed · {shell.attempts} grademe", style="#9ca3af")
			header.update(text)
			return
		exam = shell.exam
		header.border_title = f" 42pal · {exam.title} "
		text.append(f"level {shell.level} of {exam.level_count}", style="bold #e0e7ff")
		text.append(f"   {shell.mode} mode", style="#9ca3af")
		text.append(f"   grade {display.points(shell.grade)}/100", style="bold #a5b4fc")
		if shell.started_at is not None:
			left = shell._time_left()
			if shell.mode == "exam":
				style = "bold #fbbf24" if left < 10 * 60 else "#e0e7ff"
				text.append(f"   time left {display.duration(max(0, left))}", style=style)
			else:
				elapsed = shell.clock() - shell.started_at
				text.append(f"   time spent {display.duration(elapsed)}", style="#9ca3af")
		wait = shell._wait_left()
		if wait > 0:
			text.append(f"   next grademe in {display.duration(wait)}", style="#fbbf24")
		header.update(text)

	def tick(self):
		"""Each second: the header; in exam mode, the end when the time is up."""
		if self.over:
			return
		self.refresh_header()
		if not self.practice and not self.busy and self.shell._time_left() <= 0:
			self.fit_console()
			self.finish_command(*self.capture(""))

	def show_activity(self, text):
		"""Show the text of the spinner while grading, or hide it (None)."""
		activity = self.query_one("#activity", Static)
		activity.set_class(text is not None, "-busy")
		if text is not None:
			activity.update(f"⠿ {text}")

	def capture(self, command):
		"""Run `command` in the shell; return (over, what it printed, with colors)."""
		console = self.shell.console
		console.begin_capture()
		try:
			over = self.shell.handle(command)
		finally:
			printed = console.end_capture()
		return over, printed

	def on_input_submitted(self, event):
		command = event.value.strip()
		event.input.value = ""
		if self.over:
			self.dismiss(self.final)
			return
		if self.busy:
			return
		# Kept for up and down; the same command twice in a row, once.
		if command and (not self.history or self.history[-1] != command):
			self.history.append(command)
		self.history_place = None
		log = self.query_one("#log", RichLog)
		log.write(Text(f"{self.prompt} {command}", style="bold #a5b4fc"))
		# Here, not in the grading thread: the widgets belong to the screen.
		self.fit_console()
		if self.shortcuts.get(command, command) == "grademe":
			self.busy = True
			event.input.disabled = True
			self.grade_in_background(command)
		elif command == "cheat" and not self.practice:
			# Hidden: the menus of the cheat menu are screens of the app.
			self.app.cheat_flow(self)
		else:
			before = self.shell.last_report
			self.finish_command(*self.capture(command))
			# A new report goes to the clipboard too, ready to paste in an issue.
			if self.shell.last_report is not None and self.shell.last_report != before:
				self.app.copy_to_clipboard(self.shell.last_report.read_text(encoding="utf-8"))

	@work(thread=True, exclusive=True)
	def grade_in_background(self, command):
		"""A grading takes a while: it runs in a thread, the screen stays alive."""
		over, printed = self.capture(command)
		self.app.call_from_thread(self.finish_command, over, printed)

	def finish_command(self, over, printed):
		"""Show what the command printed; at the end of the exam, wait for Enter."""
		self.busy = False
		self.show_activity(None)
		command = self.query_one("#command", Input)
		command.disabled = False
		command.focus()
		log = self.query_one("#log", RichLog)
		if printed.strip():
			log.write(clickable(Text.from_ansi(printed.rstrip("\n"))))
		self.refresh_subject()
		self.refresh_header()
		if over:
			self.over = True
			self.final = printed
			command.placeholder = "Press Enter to leave"
			log.write(Text("Press Enter to leave.", style="dim"))

class Pal42App(App):
	"""42pal in full screen: login, menus, then the exam (or the practice).

	shell is a ScreenShell (or a ScreenPracticeShell with practice=True). The
	app exits with what the session printed last (the summary), for the
	terminal once the screen is gone.
	"""

	CSS_PATH = "tui.tcss"
	ENABLE_COMMAND_PALETTE = False
	TITLE = "42pal"
	# Ctrl+C copies the text selected (textual's screens do it first); with
	# nothing selected, it leaves, like Ctrl+Q.
	BINDINGS = [("ctrl+c", "quit", "Leave"), ("ctrl+q", "quit", "Leave")]
	# The clipboard programs to try (the tests put their own).
	clipboard_commands = CLIPBOARD_COMMANDS

	# How a command is started apart (the tests put their own).
	launch = staticmethod(launch)
	# The check for a newer 42pal started at launch, and the function that pulls it.
	update_check = None
	updater = staticmethod(apply_update)

	def __init__(self, shell, practice=False, theme=None, user=None):
		super().__init__()
		self.shell = shell
		self.practice = practice
		self.practice_theme = theme
		self.user = user or getpass.getuser()

	def on_mount(self):
		if self.practice:
			self.practice_flow()
		else:
			self.exam_flow()

	def copy_to_clipboard(self, text):
		"""Copy `text`: through the terminal, and with a clipboard program if there is one."""
		super().copy_to_clipboard(text)
		self.copy_with_program(text)
		lines = text.count("\n") + 1
		self.notify(f"Copied: {lines} line{'s' if lines != 1 else ''}", timeout=2)

	def copy_with_program(self, text):
		"""Give `text` to the first clipboard program found (xclip, xsel, wl-copy...)."""
		for command in self.clipboard_commands:
			if shutil.which(command[0]) is None:
				continue
			try:
				subprocess.run(command, input=text, text=True, timeout=3,
					stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			except (OSError, subprocess.TimeoutExpired):
				continue
			return

	def action_open_link(self, target):
		"""Open a file, a folder or a web page with the default application of the system."""
		program = "open" if sys.platform == "darwin" else "xdg-open"
		if self.launch is launch and shutil.which(program) is None:
			self.notify(f"Cannot open it here: {program} is missing. {target}", severity="warning")
			return
		self.launch([program, target])
		shown = target if WEB_ADDRESS.match(target) else display.short_path(target)
		self.notify(f"Opening {shown}", timeout=3)

	async def ask(self, title, items, first, highlight=0, last=None, subtitle=TAGLINE):
		"""Show a menu; return the value of the item chosen, or BACK."""
		return await self.push_screen(MenuScreen(title, items, first, highlight, last, subtitle),
			wait_for_dismiss=True)

	async def ask_progress(self):
		"""The progress: the summary under the logo, the weak themes as choices; the theme, or None."""
		store = self.shell.store
		history, grades = store.history(), store.grades()
		_, themes = self.shell._catalog()
		exams = ", ".join(f"{row.title} {display.points(row.best)}/100" for row in exam_rows(history))
		items = [(row.theme, row.theme, display.theme_score(row),
			(themes[row.theme].skill if row.theme in themes else "") + ". Practise it now.")
			for row in weak_themes(grades) if row.theme in themes]
		if not items:
			items = [("none", "No weak theme", "every theme passed", "Nothing to practise again for now.")]
		value = await self.ask("Progress", items, first=False, subtitle=summary(history, grades),
			last=("Back", f"Best grades: {exams}." if exams else "Back to the menu before."))
		return None if value in (BACK, "none") else value

	@work
	async def cheat_flow(self, screen):
		"""The cheat menu, from the session screen: the passphrase, then the menus of the pack.

		Back in a menu goes to the menu before; in the first one, back to the
		exam. What the choices print goes to the log of the session screen.
		"""
		shell = screen.shell
		passphrase = await self.push_screen(PassphraseScreen(), wait_for_dismiss=True)
		# PBKDF2 is slow on purpose: not in the loop of the screens.
		menu = await asyncio.to_thread(cheat.unlock, passphrase, shell.cheat_pack) if passphrase else None
		if menu is None:
			screen.finish_command(False, "Wrong passphrase.\n" if passphrase else "")
			return
		current, before, printed = menu.first_menu(shell), [], ""
		while True:
			title, items = current
			last = ("Back to the exam", "Close the cheat menu.") if not before else None
			value = await self.ask(title, items, first=not before, last=last)
			if value is BACK:
				if not before:
					break
				current = before.pop()
				continue
			screen.fit_console()
			shell.console.begin_capture()
			try:
				step = menu.choose(shell, value)
				if step.text:
					shell.console.print(step.text)
			finally:
				printed += shell.console.end_capture()
			if step.over or not step.menu:
				screen.finish_command(step.over, printed)
				return
			before.append(current)
			current = step.menu
		screen.finish_command(False, printed)

	def run_quietly(self, action):
		"""Run action() in the shell; what it printed is shown as a notification."""
		console = self.shell.console
		console.begin_capture()
		try:
			result = action()
		finally:
			printed = console.end_capture()
		if printed.strip():
			self.notify(Text.from_ansi(printed).plain.strip(), timeout=8)
		return result

	@work
	async def exam_flow(self):
		shell = self.shell
		shell.user = await self.push_screen(LoginScreen(self.user), wait_for_dismiss=True)
		if await self.offer_update():
			return
		if self.run_quietly(shell.restore_saved):
			if await self.ask_resume() == "resume":
				shell.show_subject()
				await self.run_session()
				return
		start = await self.choose_start()
		while start in (PRACTICE, PROGRESS):
			practice = self.practice_shell()
			if start == PROGRESS:
				theme = await self.ask_progress()
			else:
				theme = await self.choose_practice_theme(practice, first=False)
			if theme is not None:
				# The practice shell takes over: the session screen and the end use it.
				self.shell, self.practice = practice, True
				practice.theme = theme
				self.run_quietly(practice.next_subject)
				await self.run_session()
				return
			start = await self.choose_start()
		if start is None:
			self.exit()
			return
		self.run_quietly(lambda: shell.begin(*start))
		await self.run_session()

	def practice_shell(self):
		"""A practice shell with the console, workspace and catalog of the examshell."""
		shell = self.shell
		catalog, themes = shell._catalog()
		return ScreenPracticeShell(shell.console, None, shell.workspace, rng=shell.rng,
			catalog=catalog, themes=themes, sleep=shell.sleep, store=shell.store)

	async def offer_update(self):
		"""Offer the newer 42pal found at launch; return True when the app is leaving.

		Update now pulls it, then the app exits with RESTART; a failed pull is
		said, and the app goes on with this version.
		"""
		if self.update_check is None:
			return False
		# result() may wait a little for the check: not in the loop of the screens.
		update = await asyncio.to_thread(self.update_check.result)
		if update is None:
			return False
		plural = "s" if update.count != 1 else ""
		changes = "\n".join(f"· {change[:56]}" for change in update.changes[:3])
		choice = await self.ask("A new version of 42pal", [
			("update", "Update now", f"{update.count} new commit{plural}, then 42pal starts again",
				changes),
			("later", "Not now", "keep this version", "You will be asked again next time."),
		], first=True)
		if choice is BACK:
			self.exit()
			return True
		if choice == "later":
			return False
		self.notify("Updating…", timeout=3)
		ok, why = await asyncio.to_thread(self.updater)
		if not ok:
			self.notify(f"The update failed, nothing was changed: {why}", severity="error", timeout=10)
			return False
		self.exit(RESTART)
		return True

	async def ask_resume(self):
		"""Resume the saved exam, or start a new one (the saved one is abandoned)."""
		shell = self.shell
		left = shell._time_left()
		time = "no time limit" if shell.mode == "revision" else f"{display.duration(left)} left"
		choice = await self.ask("Resume your exam?", [
			("resume", "Resume", f"{shell.exam.title} · level {shell.level} · {time}",
				f"Subject: {shell.variant.name}. The time kept running while you were away."),
			("new", "Start a new exam", "the exam in progress goes to the history",
				"It is kept in the history as abandoned."),
		], first=True)
		if choice is BACK:
			self.exit()
		elif choice == "new":
			shell.abandon_saved()
		return choice

	async def choose_start(self):
		"""The menus: who, which exam, which mode, which level; None to quit.

		The last choice of each menu goes back to the one before it, skipping
		the steps that needed no menu (a single exam, the level in exam mode).
		Practice chosen in the first menu gives PRACTICE.
		"""
		steps = [self.pick_audience, self.pick_exam, self.pick_mode, self.pick_level]
		chosen = []
		# For each answer in chosen: True if a menu was shown to get it.
		shown = []
		while len(chosen) < len(steps):
			answer, asked = await steps[len(chosen)](chosen, not any(shown))
			if answer in (PRACTICE, PROGRESS):
				return answer
			if answer is BACK:
				if not any(shown):
					return None
				while not shown.pop():
					chosen.pop()
				chosen.pop()
				continue
			chosen.append(answer)
			shown.append(asked)
		_, exam, mode, level = chosen
		return exam, mode, level

	async def pick_audience(self, chosen, first):
		by_audience = {}
		for exam in self.shell._exams():
			by_audience.setdefault(exam.audience, []).append(exam)
		audiences = [audience for audience in AUDIENCES if audience in by_audience]
		items = []
		for audience in audiences:
			exams = by_audience[audience]
			meta = exams[0].title if len(exams) == 1 else f"{len(exams)} exams"
			items.append((audience, display.AUDIENCE_TEXTS[audience], meta,
				", ".join(exam.title for exam in exams)))
		if self.shell._can_practise():
			items.append((PRACTICE, display.PRACTICE_TEXT, display.PRACTICE_SUMMARY,
				"Subjects of one theme, one after the other: no timer, no wait."))
		if self.shell.store and self.shell.store.grades():
			items.append((PROGRESS, display.PROGRESS_TEXT, display.PROGRESS_SUMMARY,
				"How your exams went, and the themes that fail the most, to practise them."))
		if len(items) == 1:
			return items[0][0], False
		return await self.ask(display.FIRST_MENU_TITLE, items, first), True

	async def pick_exam(self, chosen, first):
		exams = [exam for exam in self.shell._exams() if exam.audience == chosen[0]]
		if len(exams) == 1:
			return exams[0], False
		items = [(exam, exam.title, display.exam_summary(exam),
			f"{display.points(exam.points_per_level)} points a level, 100 to pass. "
			f"{display.exam_tools(exam)}") for exam in exams]
		return await self.ask("Choose your exam", items, first), True

	async def pick_mode(self, chosen, first):
		exam = chosen[1]
		hard = ", ".join(map(display.points, exam.retry["hard"].minutes))
		soft = ", ".join(map(display.points, exam.retry["soft"].minutes))
		items = [
			("exam", "Exam", f"the real conditions · {display.exam_length(exam.duration_minutes)}",
				f"Starts at level 1. Waits after a failed grademe grow fast (minutes): {hard}."),
			("revision", "Revision", "no time limit · any starting level",
				f"Waits after a failed grademe stay short (minutes): {soft}."),
		]
		return await self.ask(f"{exam.title} · mode", items, first, highlight=1), True

	async def pick_level(self, chosen, first):
		exam, mode = chosen[1], chosen[2]
		playable = exam.playable_levels
		if mode == "exam":
			return playable[0], False
		points = display.points(exam.points_per_level)
		items = [(level, f"Level {level}", f"{points} points · {len(exam.levels[level])} styles",
			"If you start higher, the levels before it give no points.") for level in playable]
		return await self.ask(f"{exam.title} · starting level", items, first), True

	@work
	async def practice_flow(self):
		shell = self.shell
		theme = self.practice_theme
		if theme is None:
			theme = await self.choose_practice_theme(shell)
			if theme is None:
				self.exit()
				return
		shell.theme = theme
		self.run_quietly(shell.next_subject)
		await self.run_session()

	async def choose_practice_theme(self, shell, first=True):
		"""The language (when there are several), then a theme of it; None to leave.

		Back in the theme menu goes back to the language menu. first: the
		outer menu quits; otherwise (practice chosen in the first menu) it goes
		back, and None is returned too.
		"""
		_, themes = shell._catalog()
		languages = shell.practice_languages()
		asks_language = shell.language is None and len(languages) > 1
		while True:
			language = shell.language
			if asks_language:
				items = [(name, display.LANGUAGE_NAMES.get(name, name),
					f"{count} theme{'s' if count != 1 else ''}",
					"Exams: " + ", ".join(exam.title for exam in shell._exams() if exam.language == name))
					for name, count in languages.items()]
				language = await self.ask("Choose a language", items, first=first)
				if language is BACK:
					return None
			items = [(name, name, themes[name].skill,
				f"Real levels: {', '.join(f'{exam} {levels}' for exam, levels in themes[name].exams.items())}")
				for name in shell.practisable_themes(language)]
			theme = await self.ask("Choose a theme to practise", items, first=first and not asks_language)
			if theme is not BACK:
				return theme
			if not asks_language:
				return None

	async def run_session(self):
		"""The session screen until the end; then leave with what it printed last."""
		final = await self.push_screen(SessionScreen(self.shell, self.practice), wait_for_dismiss=True)
		self.exit(final)

def finish_in_terminal(final, shell, practice=False):
	"""After the full screen: the summary stays in the terminal, or how to resume."""
	console = Console()
	if final is RESTART:
		console.print("42pal is updated: it starts again.")
		restart()
	if final:
		console.print(Text.from_ansi(final.rstrip("\n")))
	elif not practice and shell.variant is not None and shell.store and shell.store.load():
		console.print("Exam stopped: run ./42pal again to resume it.")

def run_exam(workspace, store, update_check=None):
	"""42pal in full screen, on the real terminal; return the exit code.

	update_check: the check for a newer 42pal started at launch, if any.
	"""
	shell = ScreenShell(capture_console(), None, None, workspace=workspace, store=store)
	app = Pal42App(shell)
	app.update_check = update_check
	final = app.run()
	# Practice chosen in the first menu: the app ends with the practice shell.
	finish_in_terminal(final, app.shell, practice=app.practice)
	return 0

def run_practice(workspace, theme=None):
	"""Practice in full screen, on the real terminal; return the exit code.

	A theme with no exercise is said before the screen opens: exit code 1.
	"""
	shell = ScreenPracticeShell(capture_console(), None, workspace, store=SessionStore())
	choices = shell.practisable_themes()
	if theme is not None and theme not in choices:
		Console().print(f"No exercise to practise '{escape(theme)}' yet. Themes: {', '.join(choices)}")
		return 1
	final = Pal42App(shell, practice=True, theme=theme).run()
	finish_in_terminal(final, shell, practice=True)
	return 0
