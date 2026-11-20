"""word_from_end: an original program model in the style of "the last word".

The program displays a word found from the end of a string: the last but
one, the last two, the last one starting with an uppercase letter, or the
last one with a digit in it, as it is or in uppercase. The last word as it
is, a real 42 subject, is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase

LOWERCASE_TO_UPPERCASE = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def found(words, which):
	"""What `which` asks for, as one string, or None."""
	if which == "second_last":
		return words[-2] if len(words) >= 2 else None
	if which == "last_two":
		return " ".join(words[-2:]) if len(words) >= 2 else None
	if which == "last_capital":
		matching = [word for word in words if "A" <= word[0] <= "Z"]
	else:
		matching = [word for word in words if any("0" <= char <= "9" for char in word)]
	return matching[-1] if matching else None

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = [word for word in re.split("[ \t]+", test.args[0]) if word]
	result = found(words, params["which"])
	if result is None:
		return "\n"
	if params["how"] == "upper":
		result = result.translate(LOWERCASE_TO_UPPERCASE)
	return result + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase((" \t ",))]
	for text in ["  one two\tthree  ", "Hello world Foo bar", "a1 b c2d e", "alone",
			"no capital here", "Last 42 words Of 7 the day", "x yz w"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		words = ["".join(rng.choice("abXY12z") for _ in range(rng.randint(1, 6)))
			for _ in range(rng.randint(1, 6))]
		tests.append(TestCase((rng.choice([" ", "  ", "\t"]).join(words),)))
	return tests

EXERCISE = Exercise(
	name="word_from_end",
	language="c",
	kind="program",
	assignment_name="from_end_${which}_${how}",
	expected_files=("from_end_${which}_${how}.c",),
	allowed_functions=("write",),
	themes=("end_word",),
	params=(
		Param("which", ("second_last", "last_two", "last_capital", "last_digit"), {
			"second_last": "its last word but one",
			"last_two": "its last two words, in their order, separated by one space",
			"last_capital": "its last word that starts with an uppercase letter",
			"last_digit": "its last word that has a digit in it",
		}),
		Param("how", ("plain", "upper"), {
			"plain": "as it is",
			"upper": "with the lowercase letters turned into uppercase",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays\n"
		"$which,\n"
		"$how, followed by a newline.\n"
		"\n"
		"A word is a part of the string between spaces or tabs, or the start or the\n"
		"end of the string.\n"
		"\n"
		"If the number of arguments is not 1, or if there is no such word, the\n"
		"program displays only a newline."
	),
	examples=(
		TestCase(("Last 42 words Of 7 the day",)),
		TestCase(("alone",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
