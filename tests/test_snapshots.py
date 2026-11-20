"""Snapshots of a ranked exam, the client's side (plan 4.1, docs/protocol.md).

Against a fake server: the changed files only, a heartbeat when nothing
changed, a cut that leaves a gap said in the next snapshot, a broken chain
followed again, and the thread.
"""

import json
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pal42 import online
from pal42.snapshots import Snapshots

class FakeServer(BaseHTTPRequestHandler):
	"""The snapshot endpoints of docs/protocol.md."""

	received = []
	last = {"seq": 0, "hash": ""}
	down = False

	def do_POST(self):
		length = int(self.headers.get("Content-Length") or 0)
		body = json.loads(self.rfile.read(length))
		if FakeServer.down:
			return self.answer(503, {"error": "http", "message": "Down."})
		if body["previous"] != FakeServer.last["hash"]:
			return self.answer(409, {"error": "snapshot_chain", "message": "Ask for the last one."})
		self.received.append(body)
		seq = FakeServer.last["seq"] + 1
		FakeServer.last = {"seq": seq, "hash": f"h{seq}"}
		self.answer(201, FakeServer.last)

	def do_GET(self):
		self.answer(200, FakeServer.last)

	def answer(self, status, body):
		data = json.dumps(body).encode()
		self.send_response(status)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def log_message(self, *args):
		pass

class TestSnapshots(unittest.TestCase):

	def setUp(self):
		FakeServer.received = []
		FakeServer.last = {"seq": 0, "hash": ""}
		FakeServer.down = False
		server = ThreadingHTTPServer(("127.0.0.1", 0), FakeServer)
		threading.Thread(target=server.serve_forever, daemon=True).start()
		self.addCleanup(server.server_close)
		self.addCleanup(server.shutdown)
		folder = tempfile.TemporaryDirectory()
		self.addCleanup(folder.cleanup)
		self.rendu = Path(folder.name)
		api = online.Api(f"http://127.0.0.1:{server.server_port}", "tok-1")
		self.snapshots = Snapshots(api, self.read_rendu, interval=0.05)

	def read_rendu(self):
		files = {path.name: path.read_text() for path in sorted(self.rendu.glob("*.c"))}
		return "char_filter#0", files

	def write(self, text):
		(self.rendu / "only_first_chars.c").write_text(text)

	def test_only_the_changed_files_then_a_heartbeat(self):
		self.write("int main;")
		self.assertTrue(self.snapshots.send_once())
		self.assertTrue(self.snapshots.send_once())
		self.write("int main(void);")
		self.assertTrue(self.snapshots.send_once())
		files = [body["files"] for body in FakeServer.received]
		self.assertEqual(files, [{"only_first_chars.c": "int main;"}, {}, {"only_first_chars.c": "int main(void);"}])
		# Each snapshot follows the last one.
		self.assertEqual([body["previous"] for body in FakeServer.received], ["", "h1", "h2"])

	def test_a_cut_leaves_a_gap_said_in_the_next_snapshot(self):
		self.write("int a;")
		self.snapshots.send_once()
		FakeServer.down = True
		self.write("int b;")
		self.assertFalse(self.snapshots.send_once())
		self.assertFalse(self.snapshots.send_once())
		FakeServer.down = False
		self.assertTrue(self.snapshots.send_once())
		last = FakeServer.received[-1]
		self.assertEqual((last["missed"], last["files"]), (2, {"only_first_chars.c": "int b;"}))
		self.assertEqual(self.snapshots.missed, 0)

	def test_a_broken_chain_is_followed_again_with_every_file(self):
		self.write("int a;")
		self.snapshots.send_once()
		# Another terminal sent one in between.
		FakeServer.last = {"seq": 5, "hash": "h5"}
		self.assertFalse(self.snapshots.send_once())
		self.assertTrue(self.snapshots.send_once())
		last = FakeServer.received[-1]
		self.assertEqual((last["previous"], last["files"]), ("h5", {"only_first_chars.c": "int a;"}))

	def test_the_thread_sends_until_stopped_then_a_last_one(self):
		self.write("int a;")
		self.snapshots.start()
		deadline = time.monotonic() + 5
		while len(FakeServer.received) < 2 and time.monotonic() < deadline:
			time.sleep(0.01)
		self.write("int final;")
		self.snapshots.stop(final=True)
		count = len(FakeServer.received)
		self.assertGreaterEqual(count, 3)
		self.assertEqual(FakeServer.received[-1]["files"], {"only_first_chars.c": "int final;"})
		time.sleep(0.2)
		self.assertEqual(len(FakeServer.received), count)
