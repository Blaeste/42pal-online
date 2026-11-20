"""./42pal login, logout and delete-account: this terminal and the 42pal server.

login pairs the terminal with the student's 42 account: the browser does
the 42 login with the server, the terminal waits for the token
(docs/protocol.md). logout revokes the token and forgets it.
delete-account deletes the account and all its data on the server.
"""

import os
import sys
import time
import webbrowser

from rich.console import Console
from rich.markup import escape

from pal42 import online

def can_open_browser(environ=None, platform=None):
	"""True where a browser can open in a window.

	On Linux without a screen (over ssh), webbrowser would start a text
	browser inside the terminal: the link is only printed then.
	"""
	environ = os.environ if environ is None else environ
	platform = sys.platform if platform is None else platform
	return platform == "darwin" or bool(environ.get("DISPLAY") or environ.get("WAYLAND_DISPLAY"))

def login(console, server, credentials, open_browser=None, sleep=time.sleep):
	"""Log this terminal in to `server`; return the exit code.

	open_browser(url) opens the 42 login; by default the system browser,
	when there is a screen.
	"""
	saved = online.load_credentials(credentials)
	if saved and saved["server"] == server:
		console.print(f"Already logged in as {escape(saved['login'])}. To change account: ./42pal logout first.")
		return 0
	if open_browser is None and can_open_browser():
		open_browser = webbrowser.open
	api = online.Api(server)
	try:
		pairing = online.start_pairing(api)
		console.print("Log in with 42 in your browser:")
		console.print(f"  {escape(pairing['login_url'])}", soft_wrap=True)
		console.print(f"Check that the page shows the code [bold]{escape(pairing['user_code'])}[/].")
		if open_browser is not None:
			open_browser(pairing["login_url"])
		console.print("Waiting for the login… (Ctrl+C to stop)")
		answer = online.wait_for_token(api, pairing, sleep)
	except online.OnlineError as error:
		console.print(f"[red]{escape(str(error))}[/]")
		return 1
	except KeyboardInterrupt:
		console.print("\nLogin stopped.")
		return 1
	online.save_credentials(credentials, server, answer)
	campus = f" ({escape(answer['campus'])})" if answer.get("campus") else ""
	console.print(f"[green]Logged in as {escape(answer['login'])}{campus}.[/]")
	return 0

def logout(console, credentials):
	"""Revoke the token of this terminal and forget it; return the exit code."""
	saved = online.load_credentials(credentials)
	if saved is None:
		console.print("Not logged in.")
		return 0
	try:
		online.Api(saved["server"], saved["token"]).request("POST", "/logout")
		revoked = True
	except online.OnlineError as error:
		# Unknown to the server already: revoked all the same.
		revoked = error.error == "token"
		problem = str(error)
	online.delete_credentials(credentials)
	login_name = escape(saved["login"])
	if revoked:
		console.print(f"Logged out ({login_name}).")
	else:
		console.print(f"Logged out of this terminal ({login_name}), but: {escape(problem)}")
		console.print("Its token is still valid on the server: deleting your account on the site revokes it.")
	return 0

def delete_account(console, credentials, ask=input):
	"""Delete the account and all its data on the server, once the login is typed again; return the exit code."""
	saved = online.load_credentials(credentials)
	if saved is None:
		console.print("This terminal is not logged in: log in first, or delete your account on the site.")
		return 1
	login_name = saved["login"]
	console.print("This deletes your 42pal online account and all its data on the server: grades, code, "
		"snapshots. It cannot be undone.")
	try:
		typed = ask(f"Type your login ({login_name}) to confirm: ")
	except EOFError:
		typed = ""
	if typed.strip() != login_name:
		console.print("Nothing deleted.")
		return 1
	try:
		online.Api(saved["server"], saved["token"]).request("DELETE", "/account")
	except online.OnlineError as error:
		console.print(f"[red]{escape(str(error))}[/]")
		return 1
	online.delete_credentials(credentials)
	console.print("Your account and all its data are deleted. The offline modes of 42pal stay open.")
	return 0

def login_main():
	"""./42pal login."""
	return login(Console(), online.server_url(), online.CREDENTIALS)

def logout_main():
	"""./42pal logout."""
	return logout(Console(), online.CREDENTIALS)

def delete_account_main():
	"""./42pal delete-account."""
	return delete_account(Console(), online.CREDENTIALS)
