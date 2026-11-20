"""Tests of pal42.subject: writing the subject of a variant in the 42 format.

Run all the tests from the project root with: python3 -m unittest -v
"""

import subprocess
import unittest
from pathlib import Path

from pal42.model import Param, TestCase
from pal42.subject import c_char, c_string, cat_e, render, shell_quote
from pal42.variant import Variant
from tests.helpers import make_exercise

# Snapshots of subjects, reviewed once by hand, then compared at each run.
GOLDEN = Path(__file__).resolve().parent / "golden"

def repeat_oracle(params, test):
	"""Oracle of the demo exercise: the argument 2 or 3 times, or a newline."""
	if len(test.args) != 1:
		return "\n"
	count = {"twice": 2, "thrice": 3}[params["times"]]
	return " ".join([test.args[0]] * count) + "\n"

def make_repeat_exercise(**changes):
	"""A small made-up exercise, to render: display the argument 2 or 3 times."""
	fields = dict(
		name="repeat",
		assignment_name="repeat_${times}",
		expected_files=("repeat_${times}.c",),
		allowed_functions=("write",),
		params=(
			Param("times", ("twice", "thrice"), {"twice": "2 times", "thrice": "3 times"}),
		),
		subject=(
			"Write a program that takes a string and displays it $times,\n"
			"separated by spaces, followed by a newline.\n"
			"\n"
			"If the number of arguments is not 1, the program displays a newline."
		),
		oracle=repeat_oracle,
	)
	fields.update(changes)
	return make_exercise(**fields)

def repeat_twice(**changes):
	"""The variant of the demo exercise where times is "twice"."""
	return Variant(make_repeat_exercise(**changes), 0, {"times": "twice"})

def system_cat_e(data):
	"""Return what the system's `cat -e` prints for `data` (bytes)."""
	result = subprocess.run(["cat", "-e"], input=data, capture_output=True, check=True)
	return result.stdout.decode()

class TestCatE(unittest.TestCase):
	"""cat_e(text) shows a text the way `cat -e` does."""

	def test_newline_shows_as_dollar(self):
		"""Each end of line gets a `$`, so a missing \\n can be seen."""
		self.assertEqual(cat_e("hello\nworld\n"), "hello$\nworld$\n")

	def test_same_as_system_cat_e_for_every_byte(self):
		"""Invisible bytes are shown like `cat -e` does: ^A, ^?, M-a..."""
		every_byte = bytes(range(256))
		self.assertEqual(cat_e(every_byte), system_cat_e(every_byte))

class TestShellQuote(unittest.TestCase):
	"""shell_quote(arg) writes an argument the way an example shows it."""

	def test_plain_word_stays_bare_and_others_get_double_quotes(self):
		"""Like in the 42 subjects: hello stays hello, ab c becomes "ab c"."""
		self.assertEqual(shell_quote("hello"), "hello")
		self.assertEqual(shell_quote("ab c"), '"ab c"')

	def test_shell_reads_back_the_same_argument(self):
		"""An example copied into a shell gives the program the same argument."""
		for arg in ["", "ab c", 'say "hi"', "cost $5", "back\\slash", "`ls`", "*"]:
			# printf "[%s]" shows exactly the argument the shell has built.
			command = f'printf "[%s]" {shell_quote(arg)}'
			result = subprocess.run(["sh", "-c", command], capture_output=True, text=True)
			self.assertEqual(result.stdout, f"[{arg}]", command)

class TestRender(unittest.TestCase):
	"""render(variant) writes the whole subject of a variant."""

	def test_header_follows_the_42_format(self):
		"""Assignment name, Expected files and Allowed functions, then dashes."""
		lines = render(repeat_twice(allowed_functions=("write", "malloc"))).splitlines()
		self.assertEqual(lines[:4], [
			"Assignment name  : repeat_twice",
			"Expected files   : repeat_twice.c",
			"Allowed functions: write, malloc",
			"-" * 80,
		])

	def test_statement_holes_get_the_texts_of_the_values(self):
		"""Under the dashes: an empty line, then the statement, $times filled."""
		statement = render(repeat_twice()).split("-" * 80 + "\n")[1]
		self.assertEqual(statement, (
			"\n"
			"Write a program that takes a string and displays it 2 times, separated by\n"
			"spaces, followed by a newline.\n"
			"\n"
			"If the number of arguments is not 1, the program displays a newline.\n"
		))

	def test_examples_are_computed_by_the_oracle(self):
		"""Each example: the command to type, then the oracle's output in cat -e."""
		examples = (TestCase(("hello",)), TestCase(("ab c",)), TestCase())
		subject = render(repeat_twice(examples=examples))
		self.assertTrue(subject.endswith(
			"\n"
			"Examples:\n"
			"\n"
			"$>./repeat_twice hello | cat -e\n"
			"hello hello$\n"
			'$>./repeat_twice "ab c" | cat -e\n'
			"ab c ab c$\n"
			"$>./repeat_twice | cat -e\n"
			"$\n"
		), subject)

	def test_examples_can_depend_on_the_variant(self):
		"""examples(params) gives the inputs of this variant: here, a word per times."""
		def examples(params):
			return (TestCase((params["times"],)),)
		subject = render(repeat_twice(examples=examples))
		self.assertTrue(subject.endswith(
			"$>./repeat_twice twice | cat -e\n"
			"twice twice$\n"
		), subject)

class TestReflow(unittest.TestCase):
	"""The prose of a statement is wrapped at 80 columns; code stays as it is."""

	def test_lines_of_prose_are_joined_then_wrapped_at_80(self):
		"""The text of a param, put at the start of a line, no longer breaks the sentence."""
		variant = repeat_twice(subject=(
			"Write a program that takes a string and displays it\n"
			"$times,\n"
			"separated by spaces, then a newline, so that the line is longer than eighty columns."
		))
		statement = render(variant).split("-" * 80 + "\n\n")[1]
		lines = statement.splitlines()
		self.assertTrue(lines[0].startswith("Write a program that takes a string and displays it 2 times,"))
		self.assertTrue(all(len(line) <= 80 for line in lines))

	def test_a_dash_starts_an_item_of_a_list(self):
		"""Each item on its own line, wrapped under its own text; the lines of an item are joined."""
		variant = repeat_twice(subject=(
			"The rules:\n"
			"- the first rule is short;\n"
			"- the second rule is long enough that it does not fit on one line of eighty\n"
			"columns, so it goes on;\n"
			"- the last one."
		))
		statement = render(variant).split("-" * 80 + "\n\n")[1]
		self.assertEqual(statement, (
			"The rules:\n"
			"- the first rule is short;\n"
			"- the second rule is long enough that it does not fit on one line of eighty\n"
			"  columns, so it goes on;\n"
			"- the last one.\n"
		))

	def test_a_long_python_declaration_breaks_after_its_bracket(self):
		"""Not cut in the middle by the wrapping: the arguments go on an indented line."""
		variant = repeat_twice(subject="Declared as:\n\n$prototype",
			prototype=lambda name, params: f"def {name}(points: list[tuple[int, int]], height: int, width: int)"
				" -> list[str]:")
		self.assertIn("\ndef repeat_twice(\n        points: list[tuple[int, int]], height: int, width: int)"
			" -> list[str]:\n", render(variant))

	def test_arguments_too_long_for_one_line_go_on_several(self):
		"""Cut at the commas between arguments, never inside dict[str, list[str]]."""
		variant = repeat_twice(subject="Declared as:\n\n$prototype",
			prototype=lambda name, params: f"def {name}(packages: dict[str, list[str]], target: str, depth: int,"
				" names: list[str]) -> list[list[str]] | None:")
		lines = render(variant).split("Declared as:\n\n")[1].splitlines()[:3]
		self.assertEqual(lines, [
			"def repeat_twice(",
			"        packages: dict[str, list[str]], target: str, depth: int,",
			"        names: list[str]) -> list[list[str]] | None:",
		])

	def test_code_paragraphs_stay_as_they_are(self):
		"""A prototype (with a tab) and a header (with # and braces) are not wrapped."""
		variant = repeat_twice(subject=(
			"Your function must be declared as follows:\n"
			"\n"
			"char\t*$assignment(int n);\n"
			"\n"
			"#ifndef X_H\n"
			"# define X_H\n"
			"\n"
			"typedef struct s_x\n"
			"{\n"
			"\tint\tn;\n"
			"}\tt_x;"
		))
		self.assertIn("\nchar\t*repeat_twice(int n);\n\n#ifndef X_H\n# define X_H\n\ntypedef struct s_x\n{\n"
			"\tint\tn;\n}\tt_x;\n", render(variant))

class TestGolden(unittest.TestCase):
	"""The subject stays the same as a snapshot reviewed once by hand."""

	def test_subject_matches_the_reviewed_snapshot(self):
		"""The subject of repeat_twice is the one saved in tests/golden/.

		If the file is missing, the test writes it and fails: read it, and if
		it is right, run the tests again. After a wanted change of the format,
		delete the file so that the test writes it again.
		"""
		path = GOLDEN / "repeat_twice.txt"
		examples = (TestCase(("hello",)), TestCase(("ab c",)), TestCase())
		subject = render(repeat_twice(examples=examples))
		if not path.exists():
			path.parent.mkdir(exist_ok=True)
			# encoding: the campus locale may not be UTF-8 by default.
			path.write_text(subject, encoding="utf-8")
			self.fail(f"snapshot written: read {path}, then run the tests again")
		self.assertEqual(subject, path.read_text(encoding="utf-8"))

class TestCLiterals(unittest.TestCase):
	"""c_string and c_char write a test argument as C code, for a call."""

	def test_c_string_escapes_what_c_needs(self):
		"""Quotes, backslashes, newlines and tabs are escaped like in C."""
		self.assertEqual(c_string('say "hi"'), '"say \\"hi\\""')
		self.assertEqual(c_string("a\\b\n\t"), '"a\\\\b\\n\\t"')
		self.assertEqual(c_string(""), '""')

	def test_c_char_writes_one_character(self):
		"""'a', and the quote or backslash escaped."""
		self.assertEqual(c_char("a"), "'a'")
		self.assertEqual(c_char("'"), "'\\''")
		self.assertEqual(c_char("\\"), "'\\\\'")

class TestFunctionExamples(unittest.TestCase):
	"""The examples of a function: the call, then what the test main prints."""

	def test_function_examples_show_the_call_and_the_output(self):
		"""ft_count("hello", 'l') then 2$, computed by the oracle."""
		exo = make_exercise(
			name="count", kind="function", assignment_name="ft_count",
			expected_files=("ft_count.c",), harness="int\tmain(void);\n",
			subject="Count c in str.",
			oracle=lambda params, test: f"{test.args[0].count(test.args[1])}\n",
			call=lambda name, test: f"{name}({c_string(test.args[0])}, {c_char(test.args[1])})",
			examples=(TestCase(("hello", "l")), TestCase(("", "x"))),
		)
		subject = render(Variant(exo, 0, {"mode": "common"}))
		self.assertTrue(subject.endswith(
			'Examples:\n\nft_count("hello", \'l\')\n2$\nft_count("", \'x\')\n0$\n'
		), subject)

class TestGivenFiles(unittest.TestCase):
	"""Files given by the exercise are named in the header of the subject."""

	def test_the_header_names_the_given_files(self):
		"""Given files      : point.h, under Allowed functions."""
		variant = repeat_twice(provided_files={"point.h": "typedef int\tt_x;\n"})
		self.assertIn("Allowed functions: write\nGiven files      : point.h\n", render(variant))
