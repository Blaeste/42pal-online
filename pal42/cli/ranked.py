"""./42pal ranked: an exam of 42pal online, drawn, timed and graded by the server.

RankedShell is the examshell with the server as the authority. It shows the
subject the server drew, grades the rendu here first, for the trace at
once, then hands it in and shows the server's verdict, which moves the
exam on: the server's tests include some of a secret seed. The waits, the
time and the levels are the server's, the cheat menu is off, and nothing
of the exam is saved here but the traces: the server keeps it, so running
./42pal ranked again resumes it. Meanwhile, snapshots of the rendu go to
the server every 10 seconds (pal42/snapshots.py).
"""

import time

from rich.console import Console
from rich.markup import escape

from pal42 import online
from pal42.cli import display
from pal42.cli.shell import BACK, COMMANDS, Shell, terminal
from pal42.cli.workspace import Workspace
from pal42.exam import load_exam
from pal42.session import STATE_DIR
from pal42.snapshots import INTERVAL, Snapshots

# How often the shell asks whether the server has graded, and for how long.
POLL_SECONDS = 1
POLL_LIMIT_SECONDS = 600

class RankedShell(Shell):
	"""The examshell of a ranked exam (see the top of this file).

	api is the online.Api of the logged-in terminal.
	"""

	# The screens tell a ranked exam by it (no cheat menu, its own header).
	ranked = True

	def __init__(self, console, ask, api, workspace=None, clock=time.time, sleep=time.sleep, catalog=None, themes=None,
			snapshot_interval=INTERVAL):
		super().__init__(console, ask, None, workspace=workspace, clock=clock, sleep=sleep, mode="exam",
			catalog=catalog, themes=themes)
		self.api = api
		# The last state the server gave: its decisions.
		self.server_state = None
		self.snapshots = Snapshots(api, self._read_rendu, snapshot_interval)

	def run(self):
		"""Resume the exam the server has in progress, or start one; then the commands.

		Return True once an exam was played, False when none was (Back in
		the menu, an error said, Ctrl-D).
		"""
		try:
			state = self.current_state()
			if state is None:
				# The exams of the piscine for an account of the piscine, else those of the cursus.
				_, me = self.api.request("GET", "/me")
				exam = self.choose_exam("piscine" if me.get("kind") == "pool" else "student", first=True)
				if exam is BACK:
					return False
				_, state = self.api.request("POST", "/exams", {"exam": exam.id})
			else:
				self.console.print("Your ranked exam in progress resumes.")
		except online.OnlineError as error:
			self._say_error(error)
			return False
		except EOFError:
			return False
		self.start_ranked(state)
		try:
			self.command_loop()
		finally:
			# Already stopped at the end of the exam; here for Ctrl-C.
			self.snapshots.stop()
		return True

	def start_ranked(self, state):
		"""Take the exam the server gave, show its subject, start the snapshots."""
		self.follow(state)
		self.show_subject()
		self.snapshots.start()

	def current_state(self):
		"""The state of the exam in progress on the server, or None."""
		return self._current()

	def _current(self):
		"""The state of the exam in progress on the server, or None."""
		try:
			return self.api.request("GET", "/exams/current")[1]
		except online.OnlineError as error:
			if error.error == "no_exam":
				return None
			raise

	def _say_error(self, error):
		self.console.print(f"[red]{escape(str(error))}[/]")

	def follow(self, state):
		"""Take the state of the exam from the server: the level, the subject, the times."""
		catalog, themes = self._catalog()
		self.exam = load_exam(state["exam"], catalog=catalog, themes=themes)
		self.retry = self.exam.retry["hard"]
		self.level = state["level"]
		self.variant = catalog.variant(state["variant"])
		self.passed_levels = list(state["passed_levels"])
		self.attempts = state["attempts"]
		self.oks = state["oks"]
		self.failures = state["failures"]
		now = self.clock()
		self.started_at = now - state["seconds"]
		self.next_grademe_at = now + state["wait_seconds"] if state["wait_seconds"] else None
		self.server_state = state

	def grademe(self):
		"""Grade here for the trace, then hand in; the server's verdict moves the exam on.

		Return True when the exam is over.
		"""
		wait = self._wait_left()
		if wait > 0:
			self.console.print(display.wait_message(wait))
			return False
		self.console.print(display.retry_preview(self.retry.wait_after(self.failures + 1)))
		local = self._grade_and_show(self.exam.compile_command)
		# The rendu handed in is in the snapshots too, even between two ticks.
		self.snapshots.send_once()
		try:
			verdict = self._server_verdict(local.passed)
		except online.OnlineError as error:
			self._say_error(error)
			return False
		if verdict["status"] == "error":
			self.console.print(escape(verdict["trace"] or "The server could not grade: hand in again."))
			return False
		self._show_verdict(local.passed, verdict)
		state = verdict["exam"]
		self.follow(state)
		if state["ended"]:
			self.snapshots.stop()
			if state["end"] == "passed":
				self.console.print(display.exam_passed_panel(self.exam))
			elif state["end"] == "no more levels":
				self.console.print(display.no_more_levels(state["grade"]))
			self._summary(state)
			return True
		if verdict["passed"]:
			self.console.print(display.points_won(self.exam.points_per_level, state["grade"]))
			self.show_subject()
		else:
			self.console.print(display.next_grademe(state["wait_seconds"], state["wait_if_ko"]))
		return False

	def _server_verdict(self, local_passed):
		"""Hand in the files of the subject, then wait for the server's verdict."""
		_, files = self._read_rendu()
		_, queued = self.api.request("POST", "/exams/current/grademe", {"files": files, "local_passed": local_passed})
		with self._status("The server grades…"):
			for _ in range(POLL_LIMIT_SECONDS // POLL_SECONDS):
				_, verdict = self.api.request("GET", f"/grademes/{queued['grademe']}")
				if verdict["status"] in ("done", "error"):
					return verdict
				self.sleep(POLL_SECONDS)
		raise online.OnlineError("The server takes too long to grade: try grademe again later.")

	def _read_rendu(self):
		"""The current subject and the files of it found in rendu/: (variant id, {name: content})."""
		variant = self.variant
		folder = self.workspace.rendu / variant.name
		files = {}
		for name in variant.expected_files:
			if (folder / name).is_file():
				files[name] = (folder / name).read_text(encoding="utf-8", errors="replace")
		return variant.id, files

	def _show_verdict(self, local_passed, verdict):
		if verdict["passed"]:
			self.console.print("[green]Server: OK[/] — the server's tests pass too.")
		elif local_passed:
			# The trace here said OK: the server's own tests found something.
			self.console.print("[red]Server: KO[/] — OK here, KO on the server, with its extra tests:")
			self.console.print(display.trace_panel(verdict["trace"]))
		else:
			self.console.print("[red]Server: KO[/] — like here.")

	def end_exam(self, end="finish"):
		"""End the exam on the server (unless its time is up), then the summary."""
		state = self.server_state
		# The rendu as it is at the end goes in a last snapshot, while the
		# exam is still running on the server.
		self.snapshots.stop(final=end != "time")
		if end != "time":
			try:
				_, state = self.api.request("POST", "/exams/current/finish")
			except online.OnlineError as error:
				self._say_error(error)
		self._summary(state)

	def _summary(self, state):
		self.console.print(display.summary_table(
			self.exam, state["passed_levels"], state["attempts"], state["oks"], state["seconds"], state["grade"],
		))
		self.console.print("End of the ranked exam. See you soon!")

	def cheat(self):
		"""No cheat menu in a ranked exam: the command does not exist."""
		self.console.print("Unknown command: cheat. Type help for the list.")
		return False

def from_menu(console, ask, workspace, catalog=None, themes=None, credentials=None, server=None,
		open_browser=None, sleep=time.sleep):
	"""Ranked, chosen in the first menu of the examshell: log in if needed, then the exam.

	Return True once an exam was played, False to go back to the menu.
	"""
	from pal42.cli.online import login
	credentials = credentials or online.CREDENTIALS
	server = server or online.server_url()
	saved = online.load_credentials(credentials)
	if saved is None or saved["server"] != server:
		if login(console, server, credentials, open_browser=open_browser, sleep=sleep) != 0:
			return False
		saved = online.load_credentials(credentials)
	shell = RankedShell(console, ask, online.Api(saved["server"], saved["token"]), workspace=workspace,
		catalog=catalog, themes=themes)
	return shell.run()

def main(console=None, credentials=None, full_screen=False, server=None):
	"""./42pal ranked; return the exit code (1: not logged in). In full screen, the app opens on Ranked."""
	workspace = Workspace(remote=STATE_DIR / "rendu.git")
	if full_screen:
		from pal42.cli.tui import run_ranked
		return run_ranked(workspace)
	console_given = console
	if console is None:
		console, ask, _ = terminal(COMMANDS)
	else:
		ask = input
	try:
		played = from_menu(console, ask, workspace, credentials=credentials, server=server)
	except KeyboardInterrupt:
		console.print("\nExam stopped (Ctrl-C): the server keeps it; run ./42pal ranked to resume it.")
		return 130
	if not played:
		if online.load_credentials(credentials or online.CREDENTIALS) is None:
			return 1
		if console_given is None:
			console.print("Goodbye!")
	return 0
