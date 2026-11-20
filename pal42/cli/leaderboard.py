"""./42pal leaderboard: the leaderboards of the 42pal server, in the terminal.

The global score of the season (of the cursus exams, or of the piscine
exams), or the leaderboard of one exam (the best validated grade of each
student, then the shortest time), for a season and a campus if given.
Like the site, for logged-in members only.
"""

from urllib.parse import urlencode

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from pal42 import online
from pal42.cli import display

GLOBAL_TITLES = {"student": "Global score of the cursus", "piscine": "Global score of the piscine"}

def show(console, api, exam=None, season=None, campus=None, audience=None):
	"""Print the leaderboard asked; return the exit code. audience "piscine": the piscine's global score."""
	asked = (("exam", exam), ("season", season), ("campus", campus), ("audience", None if exam else audience))
	query = urlencode({key: value for key, value in asked if value})
	try:
		_, body = api.request("GET", "/leaderboard" + (f"?{query}" if query else ""))
	except online.OnlineError as error:
		console.print(f"[red]{escape(str(error))}[/]")
		return 1
	name = body["exam"] or GLOBAL_TITLES.get(body.get("audience") or "student", "Global score")
	title = f"{name} · season {body['season']}"
	if body.get("campus"):
		title += f" · {body['campus']}"
	table = Table(title=escape(title))
	table.add_column("#", justify="right")
	table.add_column("Login")
	table.add_column("Campus")
	table.add_column("Grade" if body["exam"] else "Score", justify="right")
	if body["exam"]:
		table.add_column("Time", justify="right")
	for row in body["rows"]:
		cells = [str(row["rank"]), escape(row["login"]), escape(row["campus"] or ""), display.points(row["grade"])]
		if body["exam"]:
			cells.append(display.duration(row["seconds"]))
		table.add_row(*cells)
	if not body["rows"]:
		console.print(f"{escape(title)}: no validated exam yet.")
		return 0
	console.print(table)
	return 0

def main(exam=None, season=None, campus=None, console=None, credentials=None, piscine=False):
	"""./42pal leaderboard; return the exit code."""
	console = console or Console()
	saved = online.load_credentials(credentials or online.CREDENTIALS)
	if saved is None:
		console.print("Log in first: ./42pal login")
		return 1
	return show(console, online.Api(saved["server"], saved["token"]), exam, season, campus,
		"piscine" if piscine else None)
