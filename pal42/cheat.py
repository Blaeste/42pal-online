"""The cheat menu: locked by a passphrase, its code kept encrypted.

Only the owner of 42pal has the passphrase. What the menu offers, and what
each of its choices does, is Python code encrypted in pal42/cheat.pack:
without the passphrase, reading or changing 42pal gives nothing of it. The
plain code of the menu stays on the owner's machine (cheat/, which git
ignores); `python3 -m pal42.cheat seal` encrypts it into the pack.

The key comes from the passphrase through PBKDF2-HMAC-SHA256. The code is
encrypted with HMAC-SHA256 in counter mode, then authenticated with
HMAC-SHA256 (encrypt, then MAC): a wrong passphrase or a changed byte is
found before anything is decrypted. Standard library only.

The decrypted code defines first_menu(shell), which returns the first
menu, and choose(shell, value), which runs a choice and returns a Step. A
menu is (title, items), each item (value, label, summary, details), like
the menus of the full screen.
"""

import getpass
import hashlib
import hmac
import secrets
import sys
from dataclasses import dataclass
from pathlib import Path

# The encrypted menu, next to this file, and the plain code it is made from.
PACK = Path(__file__).with_name("cheat.pack")
SOURCE = Path(__file__).resolve().parent.parent / "cheat" / "payload.py"

MAGIC = b"42PALCHEAT1\n"
# Slow on purpose: each passphrase tried costs this many rounds of SHA-256.
ITERATIONS = 600_000
SALT_SIZE = NONCE_SIZE = 16
TAG_SIZE = 32

@dataclass(frozen=True)
class Step:
	"""What a choice of the menu gives back.

	text is shown (a str or anything rich can print); menu, if any, is the
	menu to show next; over is True when the choice ended the exam.
	"""
	text: object = ""
	menu: tuple | None = None
	over: bool = False

def _keys(passphrase, salt, iterations):
	"""The key to encrypt and the key to authenticate, from the passphrase."""
	master = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations, dklen=64)
	return master[:32], master[32:]

def _stream(key, nonce, size):
	"""size bytes of HMAC-SHA256(key, nonce + counter), block after block."""
	blocks = []
	for counter in range((size + 31) // 32):
		blocks.append(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
	return b"".join(blocks)[:size]

def _xor(data, stream):
	return bytes(a ^ b for a, b in zip(data, stream))

def seal(plain, passphrase, iterations=ITERATIONS):
	"""Encrypt `plain` (bytes) with the passphrase; return the pack (bytes).

	The pack: MAGIC, salt, the number of iterations, nonce, tag, then the
	encrypted bytes. A new salt and nonce are drawn each time.
	"""
	salt, nonce = secrets.token_bytes(SALT_SIZE), secrets.token_bytes(NONCE_SIZE)
	cipher_key, mac_key = _keys(passphrase, salt, iterations)
	encrypted = _xor(plain, _stream(cipher_key, nonce, len(plain)))
	head = MAGIC + salt + iterations.to_bytes(4, "big") + nonce
	tag = hmac.new(mac_key, head + encrypted, hashlib.sha256).digest()
	return head + tag + encrypted

def open_pack(pack, passphrase):
	"""Return the bytes sealed in `pack`, or None (wrong passphrase, or a changed pack)."""
	start = len(MAGIC)
	head_size = start + SALT_SIZE + 4 + NONCE_SIZE
	if not pack.startswith(MAGIC) or len(pack) < head_size + TAG_SIZE:
		return None
	salt = pack[start:start + SALT_SIZE]
	iterations = int.from_bytes(pack[start + SALT_SIZE:start + SALT_SIZE + 4], "big")
	nonce = pack[head_size - NONCE_SIZE:head_size]
	tag, encrypted = pack[head_size:head_size + TAG_SIZE], pack[head_size + TAG_SIZE:]
	cipher_key, mac_key = _keys(passphrase, salt, iterations)
	if not hmac.compare_digest(tag, hmac.new(mac_key, pack[:head_size] + encrypted, hashlib.sha256).digest()):
		return None
	return _xor(encrypted, _stream(cipher_key, nonce, len(encrypted)))

class CheatMenu:
	"""The menu decrypted: its first menu, and what each choice does."""

	def __init__(self, namespace):
		self.first_menu = namespace["first_menu"]
		self.choose = namespace["choose"]

def unlock(passphrase, pack=None):
	"""The CheatMenu sealed in `pack` (cheat.pack by default), or None.

	None for a wrong passphrase, and when there is no pack.
	"""
	pack = Path(pack or PACK)
	if not pack.is_file():
		return None
	plain = open_pack(pack.read_bytes(), passphrase)
	if plain is None:
		return None
	namespace = {"__name__": "pal42.cheat_menu"}
	exec(compile(plain, "<cheat menu>", "exec"), namespace)
	return CheatMenu(namespace)

def _read_passphrase(prompt):
	"""From the keyboard, hidden; or a line of the standard input (the tests)."""
	if sys.stdin.isatty():
		return getpass.getpass(prompt)
	return sys.stdin.readline().rstrip("\n")

def main(args):
	"""python3 -m pal42.cheat seal [SOURCE [PACK]] | open [PACK]: encrypt or show the menu."""
	if args[:1] == ["seal"]:
		source = Path(args[1]) if len(args) > 1 else SOURCE
		pack = Path(args[2]) if len(args) > 2 else PACK
		passphrase = _read_passphrase("New passphrase: ")
		if passphrase != _read_passphrase("Again: "):
			print("The two passphrases are not the same: nothing written.", file=sys.stderr)
			return 1
		if len(passphrase) < 8:
			print("A passphrase of 8 characters at least, please (several words).", file=sys.stderr)
			return 1
		pack.write_bytes(seal(source.read_bytes(), passphrase))
		print(f"Sealed {source} into {pack}.")
		return 0
	if args[:1] == ["open"]:
		pack = Path(args[1]) if len(args) > 1 else PACK
		plain = open_pack(pack.read_bytes(), _read_passphrase("Passphrase: "))
		if plain is None:
			print("Wrong passphrase, or a changed pack.", file=sys.stderr)
			return 1
		sys.stdout.write(plain.decode())
		return 0
	print("usage: python3 -m pal42.cheat seal [SOURCE [PACK]] | open [PACK]", file=sys.stderr)
	return 2

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
