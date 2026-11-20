"""Tests of pal42.cheat: the cheat menu, locked by a passphrase, its code encrypted.

The menu itself is encrypted in pal42/cheat.pack; these tests seal made-up
menus with a made-up passphrase, and few PBKDF2 iterations to stay fast.

Run all the tests from the project root with: python3 -m unittest -v
"""

import io
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pal42.cli  # noqa: F401 (puts vendor/ on the path, for rich)
from rich.console import Console

from pal42 import cheat
from pal42.cli.shell import Shell
from pal42.cli.workspace import Workspace
from pal42.exam import load_exam
from pal42.session import SessionStore
from tests.test_cli import ECHO_CATALOG, ECHO_THEMES, Script

ROOT = Path(__file__).resolve().parent.parent

# A made-up menu: one choice that says hello, one that opens a second menu,
# and one that ends the exam. It marks the shell as cheated.
MENU = b'''
from pal42.cheat import Step

def first_menu(shell):
	return ("Made-up menu", [("hello", "Say hello", "a text", "Prints hello."),
		("more", "More", "a second menu", "Opens it."), ("end", "End", "the exam is over", "")])

def choose(shell, value):
	shell.cheated = True
	if value == "more":
		return Step(menu=("Second menu", [("deep", "Deep", "", "")]))
	if value == "end":
		return Step(text="the end", over=True)
	return Step(text=f"hello from {value}")
'''

class TestSealAndOpen(unittest.TestCase):
	def test_what_is_sealed_opens_with_the_passphrase_only(self):
		pack = cheat.seal(b"print('secret')", "correct horse", iterations=1000)
		self.assertNotIn(b"secret", pack)
		self.assertEqual(cheat.open_pack(pack, "correct horse"), b"print('secret')")
		self.assertIsNone(cheat.open_pack(pack, "wrong horse"))

	def test_a_changed_byte_makes_the_pack_unreadable(self):
		pack = bytearray(cheat.seal(b"print('secret')", "pw", iterations=1000))
		pack[-1] ^= 1
		self.assertIsNone(cheat.open_pack(bytes(pack), "pw"))
		self.assertIsNone(cheat.open_pack(b"not a pack at all", "pw"))

	def test_two_seals_of_the_same_code_differ(self):
		"""A new salt and nonce each time: nothing to compare between two packs."""
		self.assertNotEqual(cheat.seal(b"x = 1", "pw", iterations=1000), cheat.seal(b"x = 1", "pw", iterations=1000))

class TestUnlock(unittest.TestCase):
	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.pack = Path(self.tmp.name) / "cheat.pack"
		self.pack.write_bytes(cheat.seal(MENU, "pw", iterations=1000))

	def tearDown(self):
		self.tmp.cleanup()

	def test_the_right_passphrase_gives_the_menu(self):
		menu = cheat.unlock("pw", self.pack)
		title, items = menu.first_menu(None)
		self.assertEqual(title, "Made-up menu")
		self.assertEqual([item[0] for item in items], ["hello", "more", "end"])

	def test_a_wrong_passphrase_or_no_pack_gives_none(self):
		self.assertIsNone(cheat.unlock("nope", self.pack))
		self.assertIsNone(cheat.unlock("pw", Path(self.tmp.name) / "missing.pack"))

	def test_the_seal_command_reads_the_passphrase_twice_and_writes_the_pack(self):
		source = Path(self.tmp.name) / "menu.py"
		source.write_bytes(MENU)
		out = Path(self.tmp.name) / "new.pack"
		env = dict(os.environ, PYTHONPATH=str(ROOT))
		result = subprocess.run([sys.executable, "-m", "pal42.cheat", "seal", str(source), str(out)],
			input="long pass\nlong pass\n", capture_output=True, text=True, env=env, cwd=ROOT)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIsNotNone(cheat.unlock("long pass", out))
		mismatch = subprocess.run([sys.executable, "-m", "pal42.cheat", "seal", str(source), str(out)],
			input="one\ntwo\n", capture_output=True, text=True, env=env, cwd=ROOT)
		self.assertNotEqual(mismatch.returncode, 0)
		self.assertIn("not the same", mismatch.stderr + mismatch.stdout)

class TestCheatCommand(unittest.TestCase):
	"""cheat in the examshell: hidden, the passphrase, then the menus of the pack."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.pack = Path(self.tmp.name) / "cheat.pack"
		self.pack.write_bytes(cheat.seal(MENU, "pw", iterations=1000))

	def tearDown(self):
		self.tmp.cleanup()

	def shell(self, *answers, password="pw"):
		self.script = Script(*answers)
		console = Console(file=io.StringIO(), width=100, color_system=None)
		store = SessionStore(Path(self.tmp.name) / "state")
		shell = Shell(console, self.script.ask, lambda prompt: password, Workspace(Path(self.tmp.name) / "exam"),
			rng=random.Random(1), sleep=lambda seconds: None, store=store,
			catalog=ECHO_CATALOG, themes=ECHO_THEMES)
		shell.cheat_pack = self.pack
		shell.start(load_exam("rank02", catalog=ECHO_CATALOG, themes=ECHO_THEMES), 1)
		return shell

	def test_a_wrong_passphrase_shows_nothing(self):
		shell = self.shell(password="nope")
		self.assertFalse(shell.handle("cheat"))
		text = shell.console.file.getvalue()
		self.assertIn("Wrong passphrase.", text)
		self.assertNotIn("Made-up menu", text)
		self.assertFalse(shell.cheated)

	def test_a_choice_runs_then_back_to_the_exam(self):
		shell = self.shell("1")
		self.assertFalse(shell.handle("cheat"))
		text = shell.console.file.getvalue()
		self.assertIn("Made-up menu", text)
		self.assertRegex(text, r"1\. Say hello +a text")
		self.assertIn("4. Back to the exam", text)
		self.assertIn("hello from hello", text)
		self.assertTrue(shell.cheated)

	def test_back_in_a_second_menu_goes_to_the_first_one(self):
		shell = self.shell("2", "2", "4")
		self.assertFalse(shell.handle("cheat"))
		text = shell.console.file.getvalue()
		self.assertEqual(text.count("Made-up menu"), 2)
		self.assertIn("2. Back (previous menu)", text)

	def test_a_choice_can_end_the_exam_and_the_history_says_cheat(self):
		shell = self.shell("3")
		self.assertTrue(shell.handle("cheat"))
		self.assertIn("the end", shell.console.file.getvalue())
		shell.end_exam()
		self.assertTrue(shell.store.history()[-1]["cheat"])

	def test_cheat_is_not_in_the_help(self):
		shell = self.shell()
		shell.handle("help")
		self.assertNotIn("cheat", shell.console.file.getvalue())
