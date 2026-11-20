"""word_join: an original program model in the style of "clean up the spaces of a string".

The program displays the words of a string joined by a dash, a dot, a comma
and a space, or a newline, as they are or in lowercase. Joined by one
space, a real 42 subject, is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase

JOINTS = {"dash": "-", "dot": ".", "comma": ", ", "newline": "\n"}

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = [word for word in re.split("[ \t]+", test.args[0]) if word]
	if params["case"] == "lower":
		words = [word.lower() for word in words]
	return JOINTS[params["joint"]].join(words) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase((" \t ",))]
	for text in ["  Hello   big\tWorld  ", "alone", "a b", "\tTabs\t\tAND  spaces\t", "42 is THE answer"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		words = ["".join(rng.choice("abXY12") for _ in range(rng.randint(1, 5)))
			for _ in range(rng.randint(1, 5))]
		gaps = [rng.choice([" ", "  ", "\t", " \t "]) for _ in words]
		tests.append(TestCase(("".join(gap + word for gap, word in zip(gaps, words)) + rng.choice(["", " "]),)))
	return tests

EXERCISE = Exercise(
	name="word_join",
	language="c",
	kind="program",
	assignment_name="joined_${joint}_${case}",
	expected_files=("joined_${joint}_${case}.c",),
	allowed_functions=("write",),
	themes=("space_cleanup",),
	params=(
		Param("joint", ("dash", "dot", "comma", "newline"), {
			"dash": "one dash (-)",
			"dot": "one dot (.)",
			"comma": "a comma and a space (, )",
			"newline": "a newline (one word per line)",
		}),
		Param("case", ("keep", "lower"), {
			"keep": "The words are displayed as they are",
			"lower": "The uppercase letters of the words are turned into lowercase",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays its words, in their\n"
		"order, separated by\n"
		"$joint,\n"
		"followed by a newline. Nothing comes before the first word or after the\n"
		"last one.\n"
		"$case.\n"
		"\n"
		"A word is a part of the string between spaces or tabs, or the start or the\n"
		"end of the string.\n"
		"\n"
		"If the number of arguments is not 1, or if there is no word, the program\n"
		"displays only a newline."
	),
	# No tab in the examples: typed in a terminal, a tab completes a file name.
	examples=(
		TestCase(("  Hello   big  World  ",)),
		TestCase(("alone",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
