"""Command-line entry point, run by `python3 -m pal42` (see the ./42pal launcher)."""

import argparse
import sys

from pal42 import __version__

def full_screen(plain, stdin_tty, stdout_tty):
	"""True for the full-screen interface: a real terminal, and no --plain.

	Answers sent through a pipe (scripts, tests) get the text interface.
	"""
	return not plain and stdin_tty and stdout_tty

def main(argv=None):
	"""Parse the command-line arguments and return the process exit code.

	argv defaults to sys.argv[1:]; tests can pass their own list instead.
	With no command, the examshell starts.
	"""
	parser = argparse.ArgumentParser(prog="42pal")
	# The "version" action prints the string, then exits with code 0.
	# %(prog)s is replaced by the program name given above.
	parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
	parser.add_argument("--report", action="store_true",
		help="print what to paste in an issue: versions, system, exam in progress")
	plain_help = "the text interface, line by line, instead of the full screen"
	parser.add_argument("--plain", action="store_true", help=plain_help)
	commands = parser.add_subparsers(dest="command")
	check = commands.add_parser(
		"check-catalog", help="check that every ref.c passes its own exercise",
	)
	check.add_argument("names", nargs="*", metavar="EXERCISE", help="only these exercises (all by default)")
	practice = commands.add_parser(
		"practice", help="practise one theme: subjects one after the other, no timer",
	)
	practice.add_argument("--theme", help="the theme to practise (a menu if not given)")
	# SUPPRESS: ./42pal --plain practice keeps the --plain given before.
	practice.add_argument("--plain", action="store_true", default=argparse.SUPPRESS, help=plain_help)
	arguments = parser.parse_args(argv)
	if arguments.report:
		from pal42.report import report_text
		print(report_text(), end="")
		return 0
	screen = full_screen(arguments.plain, sys.stdin.isatty(), sys.stdout.isatty())
	# Imported here: --version must work even if the terminal front-end breaks.
	if arguments.command == "check-catalog":
		from pal42.cli.check import check_catalog
		return check_catalog(names=arguments.names)
	if arguments.command == "practice":
		from pal42.cli.practice import main as practice_main
		return practice_main(arguments.theme, full_screen=screen)
	# A newer 42pal is looked for while the student logs in; only when someone
	# can answer the question (not for answers sent through a pipe).
	update_check = None
	if sys.stdin.isatty():
		from pal42.update import UpdateCheck
		update_check = UpdateCheck().start()
	from pal42.cli.shell import main as shell_main
	return shell_main(full_screen=screen, update_check=update_check)

if __name__ == "__main__":
	# SystemExit turns the value returned by main() into the process exit code.
	raise SystemExit(main())
