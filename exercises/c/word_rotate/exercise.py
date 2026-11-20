"""word_rotate: an original program model in the style of "move a word of a string".

The program displays the words of a string, separated by one space, with
some moved: the first and last ones swapped, the first two moved to the
end, the longest one moved to the start, or the shortest one moved to the
end. The first word alone moved to the end, a real 42 subject, is not one
of the moves.
"""

import re

from pal42.model import Exercise, Param, TestCase

def moved(words, move):
	"""The words in their new order."""
	if move == "swap_ends":
		return [words[-1]] + words[1:-1] + [words[0]] if len(words) > 1 else words
	if move == "first_two_last":
		return words[2:] + words[:2]
	if move == "longest_first":
		chosen = max(range(len(words)), key=lambda i: len(words[i]))
		return [words[chosen]] + words[:chosen] + words[chosen + 1:]
	chosen = min(range(len(words)), key=lambda i: len(words[i]))
	return words[:chosen] + words[chosen + 1:] + [words[chosen]]

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = [word for word in re.split("[ \t]+", test.args[0]) if word]
	if not words:
		return "\n"
	return " ".join(moved(words, params["move"])) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase((" \t ",))]
	for text in ["  one two\tthree four  ", "alone", "a b", "same size word", "x yy zzz yy x"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		words = ["".join(rng.choice("abXY12") for _ in range(rng.randint(1, 6)))
			for _ in range(rng.randint(1, 6))]
		tests.append(TestCase((rng.choice([" ", "  ", "\t"]).join(words),)))
	return tests

EXERCISE = Exercise(
	name="word_rotate",
	language="c",
	kind="program",
	assignment_name="words_${move}",
	expected_files=("words_${move}.c",),
	allowed_functions=("write",),
	themes=("word_rotate",),
	params=(
		Param("move", ("swap_ends", "first_two_last", "longest_first", "shortest_last"), {
			"swap_ends": "the first word and the last one swapped",
			"first_two_last": "the first two words moved to the end, in their order",
			"longest_first": "the longest word (the first of them if several are as long) moved\n"
				"to the start",
			"shortest_last": "the shortest word (the first of them if several are as short) moved\n"
				"to the end",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays its words separated by\n"
		"one space, followed by a newline, with\n"
		"$move.\n"
		"The other words stay in their order.\n"
		"\n"
		"A word is a part of the string between spaces or tabs, or the start or the\n"
		"end of the string.\n"
		"\n"
		"If the number of arguments is not 1, or if there is no word, the program\n"
		"displays only a newline."
	),
	examples=(TestCase(("  one two three four  ",)), TestCase(("alone",)), TestCase(())),
	oracle=oracle,
	generate_tests=generate_tests,
)
