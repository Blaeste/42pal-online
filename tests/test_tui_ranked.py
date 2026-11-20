"""Ranked in the full-screen app: one app, Ranked in the first menu.

The 42 login of the terminal on its screen, the menu of Ranked, then the
ranked exam on the session screen; against the fake server of
test_ranked.py.
"""

import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from random import Random

import pal42.cli  # noqa: F401  (puts vendor/ in Python's path, for textual)
from pal42 import online
from pal42.cli.shell import RANKED
from pal42.cli.tui import LoginScreen, MenuScreen, PairingScreen, Pal42App, ScreenShell, SessionScreen, capture_console
from pal42.cli.workspace import Workspace
from pal42.themes import load_themes
from textual.widgets import OptionList
from tests.test_ranked import CATALOG, FakeServer, state
from tests.test_tui import FullScreenTest, log_text, quiet, screen_test

class RankedScreenTest(FullScreenTest):
	"""A fake 42pal server and a place for the login of the terminal."""

	def setUp(self):
		super().setUp()
		FakeServer.current = None
		FakeServer.verdict = None
		FakeServer.kind = "student"
		FakeServer.approve = True
		FakeServer.requests = []
		server = ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
		threading.Thread(target=server.serve_forever, daemon=True).start()
		self.addCleanup(server.server_close)
		self.addCleanup(server.shutdown)
		self.url = f"http://127.0.0.1:{server.server_port}"
		self.credentials = Path(self.tmp.name) / "online.json"

	def save_login(self):
		online.save_credentials(self.credentials, self.url, {"token": "tok-1", "login": "jdoe", "campus": "Mulhouse"})

	def ranked_app(self, start=None):
		shell = ScreenShell(capture_console(), None, None, Workspace(self.root), rng=Random(1), clock=self.clock,
			sleep=lambda seconds: None, store=self.store, catalog=CATALOG, themes=load_themes())
		app = quiet(Pal42App(shell, user="student", start=start))
		app.credentials = self.credentials
		app.server = self.url
		# No browser opens in the tests.
		app.launch = lambda command: None
		return app

	async def wait_for(self, pilot, condition, seconds=10):
		for _ in range(int(seconds / 0.05)):
			await pilot.pause(0.05)
			if condition():
				return
		self.fail(f"waited too long; screen: {type(pilot.app.screen).__name__} {getattr(pilot.app.screen, 'title', '')}")

	async def choose(self, pilot, value):
		"""Choose the item of the menu shown whose value is `value`."""
		screen = pilot.app.screen
		screen.query_one(OptionList).highlighted = [item[0] for item in screen.items].index(value)
		await pilot.press("enter")
		await pilot.pause()

	async def to_ranked(self, pilot):
		"""The fake login, then Ranked in the first menu."""
		await self.login(pilot)
		await self.choose(pilot, RANKED)

	def ranked_menu_shown(self, pilot):
		return isinstance(pilot.app.screen, MenuScreen) and pilot.app.screen.title.startswith("Ranked · jdoe")

	def posted(self, path):
		return [body for method, path_, body in FakeServer.requests if method == "POST" and path_ == path]

class TestRankedScreens(RankedScreenTest):

	@screen_test
	async def test_ranked_is_the_last_choice_of_the_first_menu(self):
		app = self.ranked_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.login(pilot)
			self.assertEqual(pilot.app.screen.items[-1][0], RANKED)

	@screen_test
	async def test_with_a_saved_login_ranked_starts_the_exam_on_the_session_screen(self):
		self.save_login()
		app = self.ranked_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.to_ranked(pilot)
			await self.wait_for(pilot, lambda: self.ranked_menu_shown(pilot))
			self.assertEqual(pilot.app.screen.title, "Ranked · jdoe · Mulhouse")
			# The exams of the cursus for a student, Exam Rank 02 first.
			await pilot.press("enter")
			await self.wait_for(pilot, lambda: isinstance(pilot.app.screen, SessionScreen))
			self.assertEqual(self.posted("/api/v1/exams"), [{"exam": "rank02"}])
			screen = pilot.app.screen
			self.assertIn("ranked", screen.query_one("#header").border_title)
			await self.type(pilot, "cheat")
			self.assertIn("Unknown command: cheat", log_text(screen))
			pilot.app.shell.snapshots.stop()

	@screen_test
	async def test_an_exam_in_progress_on_the_server_resumes(self):
		self.save_login()
		FakeServer.current = state(level=2, variant="char_position#3", passed_levels=[1], grade=25)
		app = self.ranked_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.to_ranked(pilot)
			await self.wait_for(pilot, lambda: self.ranked_menu_shown(pilot))
			self.assertEqual(pilot.app.screen.items[0][0], "resume")
			await pilot.press("enter")
			await self.wait_for(pilot, lambda: isinstance(pilot.app.screen, SessionScreen))
			self.assertEqual(pilot.app.shell.variant.id, "char_position#3")
			self.assertEqual(self.posted("/api/v1/exams"), [])
			pilot.app.shell.snapshots.stop()

	@screen_test
	async def test_without_a_login_the_42_login_screen_comes_first(self):
		app = self.ranked_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.to_ranked(pilot)
			await self.wait_for(pilot, lambda: isinstance(pilot.app.screen, PairingScreen))
			self.assertEqual(str(pilot.app.screen.query_one(".pairing-code").render()), "B C D F - G H J K")
			await self.wait_for(pilot, lambda: self.ranked_menu_shown(pilot))
			self.assertEqual(online.load_credentials(self.credentials)["token"], "tok-2")

	@screen_test
	async def test_escape_on_the_42_login_goes_back_to_the_first_menu(self):
		FakeServer.approve = False
		app = self.ranked_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.to_ranked(pilot)
			await self.wait_for(pilot, lambda: isinstance(pilot.app.screen, PairingScreen))
			await pilot.press("escape")
			await self.wait_for(pilot, lambda: isinstance(pilot.app.screen, MenuScreen)
				and pilot.app.screen.title == "What do you want to do?")
			self.assertFalse(self.credentials.exists())

	@screen_test
	async def test_log_out_from_the_menu_of_ranked(self):
		self.save_login()
		app = self.ranked_app()
		async with app.run_test(size=(100, 40)) as pilot:
			await self.to_ranked(pilot)
			await self.wait_for(pilot, lambda: self.ranked_menu_shown(pilot))
			await self.choose(pilot, "logout")
			await self.wait_for(pilot, lambda: pilot.app.screen.title == "What do you want to do?")
			self.assertFalse(self.credentials.exists())
			self.assertEqual(len(self.posted("/api/v1/logout")), 1)

	@screen_test
	async def test_42pal_ranked_opens_straight_on_ranked(self):
		self.save_login()
		app = self.ranked_app(start="ranked")
		async with app.run_test(size=(100, 40)) as pilot:
			await self.wait_for(pilot, lambda: self.ranked_menu_shown(pilot))
			self.assertFalse(any(isinstance(screen, LoginScreen) for screen in pilot.app.screen_stack))
			# Its last choice quits: there is no first menu to go back to.
			self.assertEqual(pilot.app.screen.last_label, "Quit")
