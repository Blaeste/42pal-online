"""Tests of the full-screen interface (pal42.cli.tui), driven by textual's pilot.

The pilot runs the app in a virtual terminal and presses keys in it; the
shells behind are the same as in the text interface.

Run all the tests from the project root with: python3 -m unittest -v
"""

import asyncio
import functools
import tempfile
import unittest
from pathlib import Path
from random import Random

import pal42.cli  # noqa: F401  (puts vendor/ in Python's path, for textual)
from pal42.cli.tui import (
	LoginScreen, MenuScreen, Pal42App, ScreenPracticeShell, ScreenShell, SessionScreen,
	capture_console,
)
from pal42.cli.workspace import Workspace
from pal42.session import Session, SessionStore
from tests.helpers import ECHO_OK
from tests.test_cli import ECHO_CATALOG, ECHO_THEMES, FakeClock

def log_text(screen):
	"""Everything the session screen wrote in its log."""
	return "\n".join(line.text for line in screen.query_one("#log").lines)

def screen_test(method):
	"""Run an async test with asyncio.run.

	unittest's IsolatedAsyncioTestCase runs its loop in debug mode, which
	makes textual several times slower.
	"""
	@functools.wraps(method)
	def run(self):
		asyncio.run(method(self))
	return run

def quiet(app):
	"""The app without its animations: the pilot would wait for each one."""
	app.animation_level = "none"
	return app

class FullScreenTest(unittest.TestCase):
	"""A temporary workspace and store for each test."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.root = Path(self.tmp.name) / "42pal_exam"
		self.store = SessionStore(Path(self.tmp.name) / ".42pal")
		self.clock = FakeClock()

	def tearDown(self):
		self.tmp.cleanup()

	def exam_app(self, catalog=ECHO_CATALOG, themes=ECHO_THEMES):
		shell = ScreenShell(capture_console(), None, None, Workspace(self.root), rng=Random(1),
			clock=self.clock, sleep=lambda seconds: None, store=self.store,
			catalog=catalog, themes=themes)
		return quiet(Pal42App(shell, user="student"))

	async def type(self, pilot, text):
		"""Type `text` in the command line, then Enter."""
		await pilot.press(*text, "enter")
		await pilot.pause()

	async def wait_grading(self, pilot, screen):
		"""Wait until the grading thread is done (10 seconds at most)."""
		for _ in range(200):
			await pilot.pause(0.05)
			if not screen.busy:
				return
		self.fail("the grading never ended")

	async def login(self, pilot):
		"""Enter twice: the login given, then any password."""
		await pilot.pause()
		await pilot.press("enter", "enter")
		await pilot.pause()

	async def login_to_exams(self, pilot):
		"""Log in, then Enter in the first menu: the exams (practice comes after them)."""
		await self.login(pilot)
		self.assertEqual(self.app_title(pilot), "What do you want to do?")
		await pilot.press("enter")
		await pilot.pause()

	def app_title(self, pilot):
		return pilot.app.screen.title

class TestExamScreens(FullScreenTest):
	"""Login, menus, then the session screen."""

	@screen_test
	async def test_login_then_mode_and_level_then_the_subject(self):
		"""One exam only: the mode menu comes first; revision asks the level."""
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await pilot.pause()
			self.assertIsInstance(app.screen, LoginScreen)
			await self.login_to_exams(pilot)
			self.assertIsInstance(app.screen, MenuScreen)
			self.assertEqual(app.screen.title, "Exam Rank 02 · mode")
			await pilot.press("enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Exam Rank 02 · starting level")
			await pilot.press("enter")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertEqual((app.shell.mode, app.shell.level), ("revision", 1))
			self.assertEqual(app.shell.user, "student")

	@screen_test
	async def test_commands_go_to_the_shell_and_their_output_to_the_log(self):
		"""status shows the level; a grademe of a right rendu passes, in a thread."""
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login_to_exams(pilot)
			await pilot.press("enter", "enter")
			await pilot.pause()
			await self.type(pilot, "s")
			self.assertRegex(log_text(app.screen), r"Level\s+1 of 4")
			rendu = self.root / "rendu" / app.shell.variant.name
			(rendu / "echo_first.c").write_text(ECHO_OK, encoding="utf-8")
			await self.type(pilot, "grademe")
			await self.wait_grading(pilot, app.screen)
			self.assertIn("OK", log_text(app.screen))
			self.assertEqual(app.shell.level, 2)

	@screen_test
	async def test_up_and_down_go_through_the_commands_typed(self):
		"""Up brings back status, then grademe... ; down goes back to what was being typed."""
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login_to_exams(pilot)
			await pilot.press("enter", "enter")
			await pilot.pause()
			command = app.screen.query_one("#command")
			await self.type(pilot, "help")
			await self.type(pilot, "status")
			await self.type(pilot, "status")
			await pilot.press("h", "e")
			await pilot.press("up")
			self.assertEqual(command.value, "status")
			await pilot.press("up")
			self.assertEqual(command.value, "help")
			await pilot.press("up")
			self.assertEqual(command.value, "help")
			await pilot.press("down", "down")
			self.assertEqual(command.value, "he")
			await pilot.press("backspace", "backspace", "up", "enter")
			await pilot.pause()
			self.assertEqual(log_text(app.screen).count("examshell> status"), 3)

	@screen_test
	async def test_exam_mode_skips_the_level_menu_and_finish_ends(self):
		"""Exam mode starts at level 1; finish, then Enter leaves with the summary."""
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login_to_exams(pilot)
			await pilot.press("up", "enter")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertEqual(app.shell.mode, "exam")
			await self.type(pilot, "finish")
			self.assertIn("End of the exam", log_text(app.screen))
			await pilot.press("enter")
			await pilot.pause()
		self.assertIn("End of the exam", app.return_value)
		self.assertEqual(self.store.history()[0]["end"], "finish")

	@screen_test
	async def test_the_menu_does_not_move_when_the_details_change(self):
		"""Exam, Revision and Back have details of different lengths: the card stays."""
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			card = app.screen.query_one(".card")
			places = set()
			for key in ["up", "down", "down", "up"]:
				await pilot.press(key)
				await pilot.pause()
				places.add((card.region.y, app.screen.query_one(".details").region.height))
			self.assertEqual(len(places), 1, places)

	@screen_test
	async def test_the_password_field_says_nothing(self):
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await pilot.pause()
			self.assertEqual(app.screen.query_one("#password").placeholder, "")

	@screen_test
	async def test_escape_in_the_first_menu_quits(self):
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			await pilot.press("escape")
			await pilot.pause()
		self.assertIsNone(app.return_value)
		self.assertIsNone(app.shell.exam)

	@screen_test
	async def test_back_goes_to_the_menu_before(self):
		"""The real exams: piscine, then Back from the exams: who are you again."""
		app = self.exam_app(catalog=None, themes=None)
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			self.assertEqual(app.screen.title, "What do you want to do?")
			await pilot.press("enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose your exam")
			await pilot.press("escape")
			await pilot.pause()
			self.assertEqual(app.screen.title, "What do you want to do?")

	@screen_test
	async def test_practice_from_the_first_menu(self):
		"""Practice, Back from the languages, Practice again, C, a theme: the practice screen."""
		app = self.exam_app(catalog=None, themes=None)
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			self.assertEqual(app.screen.title, "What do you want to do?")
			await pilot.press("down", "down", "enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose a language")
			await pilot.press("escape")
			await pilot.pause()
			self.assertEqual(app.screen.title, "What do you want to do?")
			await pilot.press("down", "down", "enter")
			await pilot.pause()
			await pilot.press("enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose a theme to practise")
			await pilot.press("enter")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertTrue(app.practice)
			self.assertEqual(app.shell.variant.exercise.language, "c")
			await self.type(pilot, "f")
			self.assertIn("Practice summary", log_text(app.screen))

	@screen_test
	async def test_a_saved_exam_can_be_resumed(self):
		"""Resume: the same level and subject as when the terminal was closed."""
		self.store.save(Session(
			exam="rank02", level=2, variant="echo_first#5", started_at=self.clock.now - 600,
			mode="exam", attempts=2, oks=1, failures=0, passed_levels=[1],
		))
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			self.assertEqual(app.screen.title, "Resume your exam?")
			await pilot.press("enter")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertEqual((app.shell.level, app.shell.variant.id), (2, "echo_first#5"))

class TestUpdateScreen(FullScreenTest):
	"""The update found at launch, offered after the login."""

	@screen_test
	async def test_update_now_pulls_then_restarts(self):
		from pal42.cli.tui import RESTART
		from pal42.update import Update
		from tests.test_cli import FakeCheck
		app = self.exam_app()
		app.update_check = FakeCheck(Update(3, ("feat: add a",)))
		pulls = []
		app.updater = lambda: pulls.append(1) or (True, "")
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			self.assertEqual(app.screen.title, "A new version of 42pal")
			await pilot.press("enter")
			for _ in range(100):
				await pilot.pause(0.05)
				if pulls and app.return_value is RESTART:
					break
		self.assertEqual(pulls, [1])
		self.assertIs(app.return_value, RESTART)

	@screen_test
	async def test_not_now_goes_to_the_menus(self):
		from pal42.update import Update
		from tests.test_cli import FakeCheck
		app = self.exam_app()
		app.update_check = FakeCheck(Update(1, ("fix: b",)))
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			await pilot.press("down", "enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "What do you want to do?")
			await pilot.press("enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Exam Rank 02 · mode")

class TestPracticeScreens(FullScreenTest):
	"""./42pal practice in full screen."""

	@screen_test
	async def test_theme_menu_then_next_subject(self):
		shell = ScreenPracticeShell(capture_console(), None, Workspace(self.root), rng=Random(1),
			catalog=ECHO_CATALOG, themes=ECHO_THEMES, sleep=lambda seconds: None)
		app = quiet(Pal42App(shell, practice=True))
		async with app.run_test(size=(100, 40)) as pilot:
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose a theme to practise")
			await pilot.press("enter")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			first = shell.variant.id
			await self.type(pilot, "n")
			self.assertNotEqual(shell.variant.id, first)
			await self.type(pilot, "f")
			self.assertIn("Practice summary", log_text(app.screen))

	@screen_test
	async def test_language_menu_then_back_from_the_themes(self):
		"""C and Python themes: the language first; Back from the themes goes back to it."""
		from pal42.catalog import Catalog
		from pal42.themes import Theme
		from tests.helpers import ECHO, make_exercise
		python_exo = make_exercise(name="py_echo", language="python", allowed_functions=(),
			themes=("py_sets",), expected_files=("py_echo.py",))
		catalog = Catalog({"echo_first": ECHO.exercise, "py_echo": python_exo}, [])
		themes = dict(ECHO_THEMES, py_sets=Theme("py_sets", "Compare in Python", {"rank03": (1,)}))
		shell = ScreenPracticeShell(capture_console(), None, Workspace(self.root), rng=Random(1),
			catalog=catalog, themes=themes, sleep=lambda seconds: None)
		app = quiet(Pal42App(shell, practice=True))
		async with app.run_test(size=(100, 40)) as pilot:
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose a language")
			await pilot.press("down", "enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose a theme to practise")
			# py_sets, then Back.
			await pilot.press("down", "enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Choose a language")
			await pilot.press("enter")
			await pilot.pause()
			await pilot.press("enter")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertEqual(shell.variant.exercise.name, "echo_first")

class TestLinks(FullScreenTest):
	"""Paths and web addresses open with a click."""

	def test_rich_links_and_web_addresses_become_clickable(self):
		"""A file link of the shell, and an https address, get a click action."""
		from rich.text import Text
		from pal42.cli.tui import clickable
		text = clickable(Text.from_markup(
			"Trace: [link=file:///tmp/x/01_a.trace]~/x/01_a.trace[/link] see https://42.fr/en now"))
		actions = {span.style.meta.get("@click") for span in text.spans
			if not isinstance(span.style, str) and span.style.meta}
		self.assertIn("app.open_link('/tmp/x/01_a.trace')", actions)
		self.assertIn("app.open_link('https://42.fr/en')", actions)

	@screen_test
	async def test_open_link_runs_the_opener_of_the_system(self):
		"""xdg-open (open on macOS) gets the path; a notification says it."""
		app = self.exam_app()
		launched = []
		app.launch = launched.append
		async with app.run_test(size=(100, 40)) as pilot:
			app.action_open_link("/tmp/somewhere")
			await pilot.pause()
		self.assertEqual(launched[0][-1], "/tmp/somewhere")
		self.assertIn(launched[0][0], ("xdg-open", "open"))

	@screen_test
	async def test_the_paths_of_the_subject_are_clickable(self):
		"""Read it and Hand in open the subject file and the rendu folder."""
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login_to_exams(pilot)
			await pilot.press("enter", "enter")
			await pilot.pause()
			where = app.screen.query_one("#subject").content
			actions = [span.style.meta["@click"] for span in where.spans
				if not isinstance(span.style, str) and "@click" in span.style.meta]
			name = app.shell.variant.name
			self.assertTrue(any(f"subjects/{name}/subject.en.txt" in action for action in actions))
			self.assertTrue(any(f"rendu/{name}" in action for action in actions))
			# A real click on the path, after "Read it  ", opens the subject.
			launched = []
			app.launch = launched.append
			await pilot.click("#subject", offset=(12, 0))
			await pilot.pause()
			self.assertTrue(launched and launched[0][-1].endswith(f"{name}/subject.en.txt"), launched)

class TestPlainLinks(unittest.TestCase):
	"""The text interface: the paths of the subject panel are terminal links."""

	def test_subject_panel_links_its_paths(self):
		from rich.console import Console
		from pal42.cli import display
		from pal42.exam import load_exam
		from pal42.variant import draw
		exam = load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		variant = draw(ECHO_CATALOG.exercises["echo_first"], 1)
		panel = display.subject_panel(exam, 1, variant, Path("/tmp/s/subject.en.txt"), Path("/tmp/r"))
		console = Console(file=__import__("io").StringIO(), force_terminal=True, width=100)
		console.print(panel)
		output = console.file.getvalue()
		self.assertIn("file:///tmp/s/subject.en.txt", output)
		self.assertIn("file:///tmp/r", output)

class TestCopy(FullScreenTest):
	"""The subject and the log can be selected and copied."""

	async def start_session(self, pilot):
		await self.login_to_exams(pilot)
		await pilot.press("enter", "enter")
		await pilot.pause()

	@screen_test
	async def test_the_subject_can_be_selected_and_copied(self):
		"""Select all of the subject, Ctrl+C: it is in the clipboard; 42pal goes on."""
		app = self.exam_app()
		copied = []
		app.clipboard_commands = [["no-such-clipboard-program"]]
		app.copy_with_program = lambda text: copied.append(text)
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			app.screen.query_one("#subject").text_select_all()
			await pilot.pause()
			self.assertIn("Assignment name  : echo_first", app.screen.get_selected_text())
			await pilot.press("ctrl+c")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertIn("Assignment name  : echo_first", app.clipboard)
			self.assertEqual(copied, [app.clipboard])

	@screen_test
	async def test_the_hints_say_how_to_copy(self):
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			hints = str(app.screen.query_one("#session-hints").render())
			self.assertIn("ctrl+c ctrl+shift+c", hints)
			self.assertIn("copy", hints)
			self.assertIn("report", hints)
			self.assertIn("r report", app.screen.query_one("#command").placeholder)

	@screen_test
	async def test_ctrl_shift_c_copies_too_and_never_leaves(self):
		"""Ctrl+Shift+C copies the selection like Ctrl+C; with nothing selected, it does nothing."""
		app = self.exam_app()
		copied = []
		app.copy_with_program = copied.append
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			await pilot.press("ctrl+shift+c")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			app.screen.query_one("#subject").text_select_all()
			await pilot.pause()
			await pilot.press("ctrl+shift+c")
			await pilot.pause()
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertIn("Assignment name  : echo_first", app.clipboard)
			self.assertEqual(copied, [app.clipboard])

	@screen_test
	async def test_the_log_can_be_selected(self):
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			await self.type(pilot, "s")
			app.screen.query_one("#log").text_select_all()
			await pilot.pause()
			self.assertRegex(app.screen.get_selected_text(), r"Level\s+1 of 4")

	@screen_test
	async def test_ctrl_c_with_nothing_selected_leaves(self):
		app = self.exam_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			await pilot.press("ctrl+c")
			await pilot.pause()
		self.assertIsNone(app.return_value)

	def test_the_first_clipboard_program_found_gets_the_text(self):
		"""A program that is not there is skipped; the next one gets the text on its input."""
		import sys
		app = self.exam_app()
		target = Path(self.tmp.name) / "clipboard.txt"
		app.clipboard_commands = [["no-such-clipboard-program"],
			[sys.executable, "-c", f"import sys; open({str(target)!r}, 'w').write(sys.stdin.read())"]]
		app.copy_with_program("int\tft_x(int n);")
		self.assertEqual(target.read_text(), "int\tft_x(int n);")

class TestLogLinks(unittest.TestCase):
	"""A link in the selectable log still opens with a click."""

	@screen_test
	async def test_a_link_in_the_log_opens_with_a_click(self):
		from rich.text import Text
		from textual.app import App
		from pal42.cli.tui import SelectableLog, clickable

		class LogApp(App):
			def __init__(self):
				super().__init__()
				self.opened = []

			def compose(self):
				yield SelectableLog(id="log", wrap=False)

			def action_open_link(self, target):
				self.opened.append(target)

		app = LogApp()
		async with app.run_test(size=(80, 10)) as pilot:
			app.query_one("#log").write(clickable(Text.from_markup(
				"Trace: [link=file:///tmp/t/01.trace]~/t/01.trace[/link]")))
			await pilot.pause()
			await pilot.click("#log", offset=(10, 0))
			await pilot.pause()
		self.assertEqual(app.opened, ["/tmp/t/01.trace"])

class TestCheatScreens(FullScreenTest):
	"""cheat in the full screen: the passphrase in a card, then the menus of the pack."""

	async def start_session(self, pilot):
		await self.login_to_exams(pilot)
		await pilot.press("enter", "enter")
		await pilot.pause()

	def sealed_app(self):
		from pal42 import cheat
		from tests.test_cheat import MENU
		app = self.exam_app()
		pack = Path(self.root).parent / "cheat.pack"
		pack.write_bytes(cheat.seal(MENU, "pw", iterations=1000))
		app.shell.cheat_pack = pack
		return app

	async def wait_for(self, pilot, condition):
		for _ in range(100):
			await pilot.pause(0.02)
			if condition():
				return

	@screen_test
	async def test_the_passphrase_then_a_choice_then_back_to_the_exam(self):
		app = self.sealed_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			session = app.screen
			await self.type(pilot, "cheat")
			self.assertEqual(app.screen.query_one(".card").border_title, " Cheat ")
			await self.type(pilot, "pw")
			await self.wait_for(pilot, lambda: app.screen.title == "Made-up menu")
			self.assertEqual(app.screen.title, "Made-up menu")
			await pilot.press("enter")
			await self.wait_for(pilot, lambda: app.screen is session)
			self.assertIs(app.screen, session)
			self.assertIn("hello from hello", log_text(session))
			self.assertTrue(app.shell.cheated)

	@screen_test
	async def test_a_wrong_passphrase_goes_back_to_the_exam(self):
		app = self.sealed_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.start_session(pilot)
			session = app.screen
			await self.type(pilot, "cheat")
			await self.type(pilot, "nope")
			await self.wait_for(pilot, lambda: app.screen is session)
			self.assertIn("Wrong passphrase.", log_text(session))
			self.assertFalse(app.shell.cheated)

class TestReportScreen(FullScreenTest):
	"""report in the full screen: the file is written, and the report goes to the clipboard."""

	@screen_test
	async def test_report_writes_the_file_and_copies_it(self):
		app = self.exam_app()
		copied = []
		app.copy_to_clipboard = copied.append
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login_to_exams(pilot)
			await pilot.press("enter", "enter")
			await pilot.pause()
			await self.type(pilot, "report")
			self.assertIn("Report written", log_text(app.screen))
			self.assertEqual(len(copied), 1)
			self.assertTrue(copied[0].startswith("# 42pal report"))


class TestProgressScreen(FullScreenTest):
	"""Progress in the first menu of the full screen: the weak themes, then practice on one."""

	@screen_test
	async def test_progress_then_a_weak_theme_to_practise(self):
		for passed in (False, True, False):
			self.store.add_grade({"variant": "word_pick#2", "themes": ["find_word"], "passed": passed,
				"source": "rank02"})
		app = self.exam_app(catalog=None, themes=None)
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			self.assertEqual(app.screen.title, "What do you want to do?")
			await pilot.press("down", "down", "down", "enter")
			await pilot.pause()
			self.assertEqual(app.screen.title, "Progress")
			self.assertIn("3 grademe · 1 OK (33%)", str(app.screen.query_one(".tagline").render()))
			await pilot.press("enter")
			for _ in range(50):
				await pilot.pause(0.02)
				if isinstance(app.screen, SessionScreen):
					break
			self.assertIsInstance(app.screen, SessionScreen)
			self.assertTrue(app.practice)
			self.assertEqual(app.shell.theme, "find_word")
