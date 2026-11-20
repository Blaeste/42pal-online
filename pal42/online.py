"""42pal online: talking to the 42pal server (docs/protocol.md).

Only the online commands load this module: the offline modes never touch
the network. urllib from the standard library, like the rest of 42pal.
Like the rest of the core, this module never prints.
"""

import json
import os
import urllib.error
import urllib.request

from pal42 import __version__
from pal42.session import STATE_DIR

# The address of the server, unless PAL42_SERVER gives another one. Until
# the domain is chosen (plan, step 0.3): a server started on this machine.
SERVER_VARIABLE = "PAL42_SERVER"
DEFAULT_SERVER = "http://127.0.0.1:8000"
# The token of this terminal: it logs in as the student, so only its owner
# may read the file.
CREDENTIALS = STATE_DIR / "online.json"
TIMEOUT = 10

class OnlineError(Exception):
	"""The server refused, or cannot be reached. The message is for the student.

	error is the code of the protocol (version, token, refused, expired...),
	or "network" when there was no answer.
	"""

	def __init__(self, message, error="network"):
		super().__init__(message)
		self.error = error

def server_url(environ=None):
	"""The address of the server: PAL42_SERVER, or DEFAULT_SERVER."""
	environ = os.environ if environ is None else environ
	return (environ.get(SERVER_VARIABLE) or DEFAULT_SERVER).rstrip("/")

class Api:
	"""The API of a 42pal server, with the token of this terminal if it has one."""

	def __init__(self, server, token=None, timeout=TIMEOUT):
		self.server = server.rstrip("/")
		self.token = token
		self.timeout = timeout

	def request(self, method, path, body=None):
		"""Send a request to /api/v1/<path>; return (status, JSON answer).

		Every request carries the version of 42pal. An error answer raises
		OnlineError with the server's message; no answer raises it too.
		"""
		data = None if body is None else json.dumps(body).encode()
		headers = {"X-42pal-Version": __version__, "Accept": "application/json"}
		if data is not None:
			headers["Content-Type"] = "application/json"
		if self.token:
			headers["Authorization"] = f"Bearer {self.token}"
		request = urllib.request.Request(f"{self.server}/api/v1{path}", data=data, headers=headers, method=method)
		try:
			with urllib.request.urlopen(request, timeout=self.timeout) as response:
				return response.status, _json(response.read())
		except urllib.error.HTTPError as error:
			answer = _json(error.read())
			raise OnlineError(answer.get("message") or f"The 42pal server answered {error.code}.",
				answer.get("error") or "http") from error
		except (urllib.error.URLError, OSError) as error:
			raise OnlineError(f"The 42pal server cannot be reached ({self.server}): "
				"check your connection, or try again later.") from error

def _json(data):
	"""The JSON object in `data`, or {} for an empty or broken answer."""
	try:
		answer = json.loads(data or b"{}")
	except ValueError:
		return {}
	return answer if isinstance(answer, dict) else {}

def start_pairing(api):
	"""Start the login of this terminal: device_code, user_code, login_url..."""
	_, answer = api.request("POST", "/pairings", {})
	if not all(key in answer for key in ("device_code", "user_code", "login_url", "interval", "expires_in")):
		raise OnlineError("The 42pal server gave an answer 42pal does not understand: update 42pal.", "request")
	return answer

def wait_for_token(api, pairing, sleep):
	"""Ask every `interval` seconds until the student confirms in the browser.

	Returns the answer with the token, the login and the campus. A refusal
	raises OnlineError; so does the end of the time the pairing lasts.
	"""
	interval = max(1, int(pairing["interval"]))
	for _ in range(max(1, int(pairing["expires_in"]) // interval)):
		sleep(interval)
		status, answer = api.request("POST", "/pairings/token", {"device_code": pairing["device_code"]})
		if status == 200 and "token" in answer:
			return answer
	raise OnlineError("The login took too long: run ./42pal login again.", "expired")

def save_credentials(path, server, answer):
	"""Keep the server, the token and the login in `path`, readable by its owner only."""
	path.parent.mkdir(parents=True, exist_ok=True)
	data = {"server": server, "token": answer["token"], "login": answer["login"], "campus": answer.get("campus")}
	# Created with the rights 600, so that it is never readable by others,
	# even for a moment; fchmod for a file that was there before.
	descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
	os.fchmod(descriptor, 0o600)
	with os.fdopen(descriptor, "w") as file:
		file.write(json.dumps(data, indent=2) + "\n")

def load_credentials(path):
	"""What save_credentials kept, or None if this terminal is not logged in."""
	try:
		data = json.loads(path.read_text())
	except (OSError, ValueError):
		return None
	if not isinstance(data, dict) or not all(isinstance(data.get(key), str) for key in ("server", "token", "login")):
		return None
	return data

def delete_credentials(path):
	"""Forget the token of this terminal."""
	try:
		path.unlink()
	except FileNotFoundError:
		pass
