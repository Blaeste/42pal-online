"""42pal online in the client: ./42pal login and logout (docs/protocol.md).

Against a fake 42pal server on a local port. The last tests check that the
offline modes never touch the network, nor even load the online module.
"""

import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pal42 import __version__, online
# Imported before rich: pal42.cli puts vendor/, where rich is, on the path.
from pal42.cli import online as online_cli
from rich.console import Console

ROOT = Path(__file__).resolve().parent.parent
# Port 9 of the local machine: nothing listens there.
NOWHERE = "http://127.0.0.1:9"

class FakeServer(BaseHTTPRequestHandler):
	"""The API of the 42pal server, as docs/protocol.md says. Each test sets it."""

	version = __version__
	pending_polls = 1
	expires_in = 600
	token_answer = (200, {"token": "tok-1", "login": "jdoe", "campus": "Mulhouse"})
	requests = []

	def do_POST(self):
		length = int(self.headers.get("Content-Length") or 0)
		body = json.loads(self.rfile.read(length) or b"null")
		self.requests.append((self.path, self.headers.get("X-42pal-Version"), self.headers.get("Authorization"), body))
		if self.headers.get("X-42pal-Version") != self.version:
			message = f"This server needs 42pal {self.version}: update 42pal (git pull), then try again."
			return self.answer(426, {"error": "version", "message": message})
		if self.path == "/api/v1/pairings":
			return self.answer(201, {
				"device_code": "dev-1", "user_code": "BCDF-GHJK", "login_url": "http://server/pair/BCDF-GHJK",
				"interval": 2, "expires_in": self.expires_in,
			})
		if self.path == "/api/v1/pairings/token":
			if FakeServer.pending_polls > 0:
				FakeServer.pending_polls -= 1
				return self.answer(202, {"status": "pending"})
			return self.answer(*self.token_answer)
		if self.path == "/api/v1/logout":
			return self.answer(204, None)
		self.answer(404, {"error": "request", "message": "Unknown request."})

	def answer(self, status, body):
		data = b"" if body is None else json.dumps(body).encode()
		self.send_response(status)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def log_message(self, *args):
		pass

class OnlineTestCase(unittest.TestCase):
	"""A fake server, a temporary ~/.42pal/online.json, a console to read."""

	def setUp(self):
		FakeServer.version = __version__
		FakeServer.pending_polls = 1
		FakeServer.expires_in = 600
		FakeServer.token_answer = (200, {"token": "tok-1", "login": "jdoe", "campus": "Mulhouse"})
		FakeServer.requests = []
		server = ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
		threading.Thread(target=server.serve_forever, daemon=True).start()
		self.addCleanup(server.server_close)
		self.addCleanup(server.shutdown)
		self.url = f"http://127.0.0.1:{server.server_port}"
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		self.credentials = Path(folder.name) / ".42pal" / "online.json"
		self.console = Console(file=io.StringIO(), width=200, color_system=None)
		self.opened = []
		self.slept = []

	def login(self, server=None):
		return online_cli.login(self.console, server or self.url, self.credentials,
			open_browser=self.opened.append, sleep=self.slept.append)

	def logout(self):
		return online_cli.logout(self.console, self.credentials)

	def output(self):
		return self.console.file.getvalue()

class TestLogin(OnlineTestCase):
	"""./42pal login."""

	def test_login_pairs_and_keeps_the_token_readable_by_its_owner_only(self):
		self.assertEqual(self.login(), 0)
		text = self.output()
		self.assertIn("http://server/pair/BCDF-GHJK", text)
		self.assertIn("BCDF-GHJK", text)
		self.assertIn("Logged in as jdoe (Mulhouse)", text)
		self.assertEqual(self.opened, ["http://server/pair/BCDF-GHJK"])
		# One poll pending, then the token: two waits of `interval` seconds.
		self.assertEqual(self.slept, [2, 2])
		saved = json.loads(self.credentials.read_text())
		self.assertEqual(saved, {"server": self.url, "token": "tok-1", "login": "jdoe", "campus": "Mulhouse"})
		self.assertEqual(stat.S_IMODE(self.credentials.stat().st_mode), 0o600)
		self.assertTrue(all(version == __version__ for _, version, _, _ in FakeServer.requests))
		self.assertEqual(FakeServer.requests[1][3], {"device_code": "dev-1"})

	def test_a_refused_login_says_why_and_keeps_nothing(self):
		FakeServer.token_answer = (403, {"error": "refused", "message": "Ranked mode is for students of the 42 cursus."})
		self.assertEqual(self.login(), 1)
		self.assertIn("Ranked mode is for students of the 42 cursus.", self.output())
		self.assertFalse(self.credentials.exists())

	def test_another_version_says_to_update(self):
		FakeServer.version = "9.9.9"
		self.assertEqual(self.login(), 1)
		self.assertIn("update 42pal", self.output())
		self.assertEqual(self.opened, [])

	def test_a_server_out_of_reach_is_said(self):
		self.assertEqual(self.login(NOWHERE), 1)
		self.assertIn("cannot be reached", self.output())

	def test_the_login_stops_when_the_pairing_expires(self):
		FakeServer.pending_polls = 1000
		FakeServer.expires_in = 6
		self.assertEqual(self.login(), 1)
		self.assertIn("run ./42pal login again", self.output())
		self.assertEqual(self.slept, [2, 2, 2])

	def test_already_logged_in_asks_nothing(self):
		online.save_credentials(self.credentials, self.url, {"token": "t", "login": "jdoe", "campus": None})
		self.assertEqual(self.login(), 0)
		self.assertIn("Already logged in as jdoe", self.output())
		self.assertEqual(FakeServer.requests, [])

	def test_a_message_of_the_server_is_not_read_as_markup(self):
		"""The server's sentence is shown as it is, even with [brackets]."""
		FakeServer.token_answer = (403, {"error": "refused", "message": "Refused [bold]really[/bold]."})
		self.login()
		self.assertIn("Refused [bold]really[/bold].", self.output())

class TestLogout(OnlineTestCase):
	"""./42pal logout."""

	def test_logout_revokes_the_token_and_deletes_the_file(self):
		online.save_credentials(self.credentials, self.url, {"token": "tok-1", "login": "jdoe", "campus": None})
		self.assertEqual(self.logout(), 0)
		self.assertEqual(FakeServer.requests[0][:3], ("/api/v1/logout", __version__, "Bearer tok-1"))
		self.assertFalse(self.credentials.exists())
		self.assertIn("Logged out (jdoe)", self.output())

	def test_logout_without_the_server_deletes_the_file_and_warns(self):
		online.save_credentials(self.credentials, NOWHERE, {"token": "tok-1", "login": "jdoe", "campus": None})
		self.assertEqual(self.logout(), 0)
		self.assertFalse(self.credentials.exists())
		self.assertIn("still valid on the server", self.output())

	def test_logout_when_not_logged_in(self):
		self.assertEqual(self.logout(), 0)
		self.assertIn("Not logged in", self.output())

class TestBrowser(unittest.TestCase):
	"""The browser opens only where there is a screen: never a text browser in the terminal."""

	def test_a_browser_needs_a_display_on_linux(self):
		self.assertTrue(online_cli.can_open_browser({"DISPLAY": ":0"}, "linux"))
		self.assertTrue(online_cli.can_open_browser({"WAYLAND_DISPLAY": "wayland-0"}, "linux"))
		self.assertFalse(online_cli.can_open_browser({}, "linux"))
		self.assertTrue(online_cli.can_open_browser({}, "darwin"))

# Written as sitecustomize.py in a folder of PYTHONPATH: Python runs it at
# start. Its audit hook writes down, then stops, any network use and any
# import of the online module.
NO_NETWORK = '''
import sys
MARKER = {marker!r}
def no_network(event, args):
	if event in ("socket.connect", "socket.getaddrinfo") or (event == "import" and args[0] == "pal42.online"):
		with open(MARKER, "a") as file:
			file.write(event + " " + str(args[0]) + "\\n")
		raise RuntimeError("an offline mode used the network: " + event)
sys.addaudithook(no_network)
'''

class TestOfflineModesStayOffline(unittest.TestCase):
	"""The offline modes open no connection, and do not even load pal42.online."""

	def run_blocked(self, command, answers=""):
		"""Run `command` with the network blocked; return the process and what was blocked."""
		with tempfile.TemporaryDirectory() as folder:
			site = Path(folder) / "site"
			site.mkdir()
			marker = Path(folder) / "blocked.txt"
			(site / "sitecustomize.py").write_text(NO_NETWORK.format(marker=str(marker)))
			result = subprocess.run(
				command, input=answers, capture_output=True, text=True, timeout=60,
				env=dict(os.environ, HOME=folder, PYTHONPATH=str(site)), start_new_session=True,
			)
			blocked = marker.read_text() if marker.exists() else ""
		return result, blocked

	def test_the_block_works(self):
		"""Without this, the tests below could pass for nothing."""
		_, blocked = self.run_blocked([sys.executable, "-c", "import socket; socket.getaddrinfo('localhost', 80)"])
		self.assertIn("socket.getaddrinfo", blocked)

	def test_the_examshell_stays_offline(self):
		result, blocked = self.run_blocked([str(ROOT / "42pal")], "\npw\n2\n1\n\n\nstatus\nfinish\n")
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn("End of the exam", result.stdout)
		self.assertEqual(blocked, "")

	def test_practice_stays_offline(self):
		result, blocked = self.run_blocked([str(ROOT / "42pal"), "practice", "--theme", "common_chars"], "finish\n")
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertEqual(blocked, "")
