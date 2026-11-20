"""./42pal ranked: the examshell of a ranked exam, against a fake 42pal server.

The server draws, times and decides; the shell grades here first for the
trace, then shows the server's verdict (plan 3.4).
"""

import io
import json
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pal42 import online
from pal42.catalog import load_catalog
# Imported before rich: pal42.cli puts vendor/, where rich is, on the path.
from pal42.cli import ranked
from pal42.cli.workspace import Workspace
from rich.console import Console

CATALOG = load_catalog()
FIRST = "char_filter#0"
SECOND = "char_position#3"

def state(variant=FIRST, level=1, **changes):
	"""A state of a ranked exam of rank02, as the server sends it."""
	answer = {
		"exam": "rank02", "title": "Exam Rank 02", "level": level, "variant": variant, "seconds": 60,
		"seconds_left": 10740, "failures": 0, "wait_seconds": 0, "wait_if_ko": 30, "attempts": 0, "oks": 0,
		"passed_levels": [], "grade": 0, "grading": None, "ended": False, "end": None,
	}
	answer.update(changes)
	return answer

class FakeServer(BaseHTTPRequestHandler):
	"""The ranked exam API of docs/protocol.md; each test sets what it answers."""

	current = None
	verdict = None
	requests = []

	def do_GET(self):
		self.requests.append(("GET", self.path, None))
		if self.path == "/api/v1/exams/current":
			if FakeServer.current is None:
				return self.answer(404, {"error": "no_exam", "message": "No ranked exam in progress."})
			return self.answer(200, FakeServer.current)
		if self.path == "/api/v1/exams/current/snapshots/last":
			return self.answer(200, {"seq": 0, "hash": ""})
		if self.path == "/api/v1/grademes/1":
			# Once still running, then the verdict.
			if not any(path == "/api/v1/grademes/1" for _, path, _ in self.requests[:-1]):
				return self.answer(200, {"status": "running"})
			return self.answer(200, FakeServer.verdict)
		self.answer(404, {"error": "unknown", "message": "Unknown."})

	def do_POST(self):
		length = int(self.headers.get("Content-Length") or 0)
		body = json.loads(self.rfile.read(length) or b"null")
		self.requests.append(("POST", self.path, body))
		if self.path == "/api/v1/exams":
			FakeServer.current = state()
			return self.answer(201, FakeServer.current)
		if self.path == "/api/v1/exams/current/grademe":
			return self.answer(202, {"grademe": 1})
		if self.path == "/api/v1/exams/current/snapshots":
			count = sum(path == self.path for _, path, _ in self.requests)
			return self.answer(201, {"seq": count, "hash": f"h{count}"})
		if self.path == "/api/v1/exams/current/finish":
			return self.answer(200, state(ended=True, end="finish", seconds=600, attempts=1))
		self.answer(404, {"error": "unknown", "message": "Unknown."})

	def answer(self, status, body):
		data = json.dumps(body).encode()
		self.send_response(status)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def log_message(self, *args):
		pass

def right_rendu(variant_id):
	"""The ref.c of a variant, its -D flags written as #define lines."""
	variant = CATALOG.variant(variant_id)
	ref = (CATALOG.folders[variant.exercise.name] / "ref.c").read_text()
	defines = "".join("#define " + flag[2:].replace("=", " ", 1) + "\n" for flag in variant.defines)
	return defines + ref

class RankedTestCase(unittest.TestCase):

	def setUp(self):
		FakeServer.current = None
		FakeServer.verdict = None
		FakeServer.requests = []
		server = ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
		threading.Thread(target=server.serve_forever, daemon=True).start()
		self.addCleanup(server.server_close)
		self.addCleanup(server.shutdown)
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		self.root = Path(folder.name)
		self.api = online.Api(f"http://127.0.0.1:{server.server_port}", "tok-1")
		self.console = Console(file=io.StringIO(), width=120, color_system=None)
		self.prompts = []

	def run_shell(self, *answers):
		answers = list(answers)

		def ask(prompt, default=None):
			self.prompts.append(prompt)
			if not answers:
				raise EOFError
			return answers.pop(0)

		shell = ranked.RankedShell(self.console, ask, self.api, workspace=Workspace(self.root),
			sleep=lambda seconds: None, catalog=CATALOG)
		shell.run()
		return shell

	def hand_in(self, variant_id, code):
		variant = CATALOG.variant(variant_id)
		folder = self.root / "rendu" / variant.name
		folder.mkdir(parents=True, exist_ok=True)
		(folder / variant.expected_files[0]).write_text(code)

	def output(self):
		return self.console.file.getvalue()

	def posted(self, path):
		return [body for method, path_, body in FakeServer.requests if method == "POST" and path_ == path]

class TestRankedShell(RankedTestCase):

	def test_both_ok_gives_the_next_level_drawn_by_the_server(self):
		self.hand_in(FIRST, right_rendu(FIRST))
		FakeServer.verdict = {"status": "done", "passed": True, "trace": "", "tests_passed": 20, "tests_total": 20,
			"exam": state(SECOND, level=2, passed_levels=[1], grade=25, oks=1, attempts=1)}
		shell = self.run_shell("1", "grademe")
		self.assertEqual(self.posted("/api/v1/exams"), [{"exam": "rank02"}])
		[handed] = self.posted("/api/v1/exams/current/grademe")
		name = CATALOG.variant(FIRST).expected_files[0]
		self.assertEqual(handed, {"files": {name: right_rendu(FIRST)}, "local_passed": True})
		text = self.output()
		self.assertIn("Server: OK", text)
		self.assertEqual((shell.level, shell.variant.id, shell.passed_levels), (2, SECOND, [1]))
		self.assertTrue((self.root / "subjects" / CATALOG.variant(SECOND).name).is_dir())

	def test_ok_here_but_ko_on_the_server_shows_the_server_trace_and_its_wait(self):
		self.hand_in(FIRST, right_rendu(FIRST))
		FakeServer.verdict = {"status": "done", "passed": False, "trace": "Test 21: wrong output (server)",
			"tests_passed": 20, "tests_total": 25, "exam": state(failures=1, wait_seconds=30, wait_if_ko=150, attempts=1)}
		shell = self.run_shell("1", "grademe", "grademe")
		text = self.output()
		self.assertIn("OK here, KO on the server", text)
		self.assertIn("Test 21: wrong output (server)", text)
		self.assertEqual((shell.level, shell.variant.id, shell.failures), (1, FIRST, 1))
		# The second grademe comes too early: refused here, nothing sent.
		self.assertEqual(len(self.posted("/api/v1/exams/current/grademe")), 1)

	def test_an_exam_in_progress_on_the_server_resumes_without_menu(self):
		FakeServer.current = state(level=2, variant=SECOND, passed_levels=[1], grade=25)
		shell = self.run_shell("status")
		self.assertNotIn("Exam:", self.prompts)
		self.assertIn("resumes", self.output())
		self.assertEqual(shell.variant.id, SECOND)
		self.assertEqual(self.posted("/api/v1/exams"), [])

	def test_finish_ends_the_exam_on_the_server(self):
		self.run_shell("1", "finish")
		self.assertEqual(len(self.posted("/api/v1/exams/current/finish")), 1)
		self.assertIn("End of the ranked exam", self.output())

	def test_snapshots_go_while_the_exam_runs_and_a_last_one_before_finish(self):
		self.hand_in(FIRST, "int\tmain(void);\n")
		self.run_shell("1", "finish")
		paths = [path for method, path, _ in FakeServer.requests if method == "POST"]
		self.assertIn("/api/v1/exams/current/snapshots", paths)
		last_snapshot = max(i for i, path in enumerate(paths) if path == "/api/v1/exams/current/snapshots")
		self.assertLess(last_snapshot, paths.index("/api/v1/exams/current/finish"))
		name = CATALOG.variant(FIRST).expected_files[0]
		sent = [body["files"] for body in self.posted("/api/v1/exams/current/snapshots")]
		self.assertIn({name: "int\tmain(void);\n"}, sent)

	def test_a_snapshot_of_the_rendu_goes_just_before_each_grademe(self):
		"""The rendu is written after the first snapshot: only the one before grademe can hold it."""
		FakeServer.verdict = {"status": "done", "passed": False, "trace": "KO", "tests_passed": 0, "tests_total": 1,
			"exam": state(failures=1, wait_seconds=30, attempts=1)}
		answers = ["1", "grademe"]

		def ask(prompt, default=None):
			if prompt == "examshell>" and answers == ["grademe"]:
				deadline = time.monotonic() + 5
				while not self.posted("/api/v1/exams/current/snapshots") and time.monotonic() < deadline:
					time.sleep(0.01)
				self.hand_in(FIRST, right_rendu(FIRST))
			if not answers:
				raise EOFError
			return answers.pop(0)

		ranked.RankedShell(self.console, ask, self.api, workspace=Workspace(self.root), sleep=lambda seconds: None,
			catalog=CATALOG).run()
		posts = [(path, body) for method, path, body in FakeServer.requests if method == "POST"]
		grademe = [path for path, _ in posts].index("/api/v1/exams/current/grademe")
		name = CATALOG.variant(FIRST).expected_files[0]
		before = [body["files"] for path, body in posts[:grademe] if path == "/api/v1/exams/current/snapshots"]
		self.assertIn({name: right_rendu(FIRST)}, before)

	def test_the_cheat_menu_is_off(self):
		self.run_shell("1", "cheat")
		self.assertIn("Unknown command: cheat", self.output())

class TestRankedCommand(unittest.TestCase):

	def test_ranked_needs_a_login_first(self):
		with tempfile.TemporaryDirectory() as folder:
			console = Console(file=io.StringIO(), width=120, color_system=None)
			code = ranked.main(console=console, credentials=Path(folder) / "online.json")
		self.assertEqual(code, 1)
		self.assertIn("./42pal login", console.file.getvalue())
