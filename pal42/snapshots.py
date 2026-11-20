"""Snapshots of a ranked exam, the client's side (docs/protocol.md).

Every few seconds a thread sends the server the files of the subject that
changed since the last snapshot it kept, or none (a heartbeat: the server
sees the terminal is there). A send that fails is counted and said in the
next one, which carries every change since: the server sees the gap, and
nothing is lost. Like the rest of the core, this module never prints.
"""

import threading

from pal42.online import OnlineError

# Seconds between two snapshots.
INTERVAL = 10

class Snapshots:
	"""The snapshots of one exam. read_rendu() gives (variant id, {name: content})."""

	def __init__(self, api, read_rendu, interval=INTERVAL):
		self.api = api
		self.read_rendu = read_rendu
		self.interval = interval
		# The last link of the chain the server gave.
		self.seq = 0
		self.last_hash = ""
		# What the server has of each file, by (variant, name): only changes go.
		self.acknowledged = {}
		# Sends that failed since the last one the server kept.
		self.missed = 0
		self.over = False
		# The thread and the shell (before a grademe) both send: one at a time.
		self._lock = threading.Lock()
		self._stop = threading.Event()
		self._thread = None

	def send_once(self):
		"""Send one snapshot; return True if the server kept it."""
		with self._lock:
			return self._send()

	def _send(self):
		variant, files = self.read_rendu()
		changed = {name: content for name, content in files.items() if self.acknowledged.get((variant, name)) != content}
		body = {"seq": self.seq + 1, "previous": self.last_hash, "variant": variant, "files": changed,
			"missed": self.missed}
		try:
			_, answer = self.api.request("POST", "/exams/current/snapshots", body)
		except OnlineError as error:
			if error.error == "snapshot_chain":
				self.follow_again()
			elif error.error == "no_exam":
				self.over = True
			# busy (too often) and variant (the subject just changed) are no gap.
			elif error.error not in ("busy", "variant"):
				self.missed += 1
			return False
		self.seq = answer["seq"]
		self.last_hash = answer["hash"]
		for name, content in changed.items():
			self.acknowledged[(variant, name)] = content
		self.missed = 0
		return True

	def follow_again(self):
		"""Take the server's last link (a new terminal, a broken chain); send every file again."""
		try:
			_, last = self.api.request("GET", "/exams/current/snapshots/last")
		except OnlineError:
			self.missed += 1
			return
		self.seq = last["seq"]
		self.last_hash = last["hash"]
		self.acknowledged = {}

	def start(self):
		"""Follow the server's chain, then send one snapshot now and one every `interval` seconds."""
		self.follow_again()

		def run():
			self.send_once()
			while not self.over and not self._stop.wait(self.interval):
				self.send_once()

		self._thread = threading.Thread(target=run, name="42pal-snapshots", daemon=True)
		self._thread.start()

	def stop(self, final=False):
		"""Stop the thread; final sends the rendu one last time (before finish)."""
		self._stop.set()
		if self._thread is not None:
			self._thread.join(timeout=30)
		if final and not self.over:
			self.send_once()
