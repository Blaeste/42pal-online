"""./42pal leaderboard: the leaderboard of the server, in the terminal (plan 7.3)."""

import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from pal42 import online
# Imported before rich: pal42.cli puts vendor/, where rich is, on the path.
from pal42.cli import leaderboard
from rich.console import Console

ROWS = [
	{"rank": 1, "login": "bob", "campus": "Paris", "grade": 75, "seconds": 6000},
	{"rank": 2, "login": "ann", "campus": "Mulhouse", "grade": 75, "seconds": 7200},
]

class FakeServer(BaseHTTPRequestHandler):
	asked = []

	def do_GET(self):
		parts = urlsplit(self.path)
		query = {key: values[0] for key, values in parse_qs(parts.query).items()}
		self.asked.append((parts.path, query, self.headers.get("Authorization")))
		audience = None if query.get("exam") else query.get("audience", "student")
		# The promo of the token's student by default; all: every promo.
		promo = None if query.get("promo") == "all" else query.get("promo", "2024-07")
		body = {"exam": query.get("exam"), "audience": audience, "promo": promo, "campus": query.get("campus"),
			"rows": ROWS if query.get("exam") else [dict(row, seconds=None) for row in ROWS]}
		data = json.dumps(body).encode()
		self.send_response(200)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def log_message(self, *args):
		pass

class TestLeaderboard(unittest.TestCase):

	def setUp(self):
		FakeServer.asked = []
		server = ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
		threading.Thread(target=server.serve_forever, daemon=True).start()
		self.addCleanup(server.server_close)
		self.addCleanup(server.shutdown)
		self.api = online.Api(f"http://127.0.0.1:{server.server_port}", "tok-1")
		self.console = Console(file=io.StringIO(), width=120, color_system=None)

	def test_the_leaderboard_of_an_exam(self):
		self.assertEqual(leaderboard.show(self.console, self.api, exam="rank02", promo="2023-09", campus="Paris"), 0)
		path, query, authorization = FakeServer.asked[0]
		self.assertEqual((path, query, authorization),
			("/api/v1/leaderboard", {"exam": "rank02", "promo": "2023-09", "campus": "Paris"}, "Bearer tok-1"))
		text = self.console.file.getvalue()
		self.assertIn("rank02", text)
		self.assertIn("September 2023", text)
		self.assertRegex(text, r"1\s+│?\s*bob\s+│?\s*Paris\s+│?\s*75")
		self.assertIn("1:40:00", text)

	def test_the_global_score_of_the_student_s_promo_has_no_time(self):
		leaderboard.show(self.console, self.api)
		self.assertEqual(FakeServer.asked[0][1], {})
		text = self.console.file.getvalue()
		self.assertIn("Global score of the cursus", text)
		self.assertIn("July 2024", text)
		self.assertNotIn("1:40:00", text)

	def test_every_promo(self):
		leaderboard.show(self.console, self.api, exam="rank02", promo="all")
		self.assertEqual(FakeServer.asked[0][1], {"exam": "rank02", "promo": "all"})
		self.assertIn("every promo", self.console.file.getvalue())

	def test_the_global_score_of_the_piscine(self):
		leaderboard.show(self.console, self.api, audience="piscine")
		self.assertEqual(FakeServer.asked[0][1], {"audience": "piscine"})
		self.assertIn("Global score of the piscine", self.console.file.getvalue())

	def test_it_needs_a_login(self):
		with tempfile.TemporaryDirectory() as folder:
			console = Console(file=io.StringIO(), width=120, color_system=None)
			self.assertEqual(leaderboard.main(console=console, credentials=Path(folder) / "online.json"), 1)
		self.assertIn("./42pal login", console.file.getvalue())

	def test_a_server_out_of_reach_is_said(self):
		self.assertEqual(leaderboard.show(self.console, online.Api("http://127.0.0.1:9", "t")), 1)
		self.assertIn("cannot be reached", self.console.file.getvalue())
