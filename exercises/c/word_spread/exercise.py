"""word_spread: an original program model in the style of "spread the words of a string".

The program displays the words of a string separated by two spaces, four
spaces or a tab, between the words only or around them too. Three spaces
between the words only, a real 42 subject, are never the gap.
"""

import re

from pal42.model import Exercise, Param, TestCase

GAPS = {"2": "  ", "4": "    ", "tab": "\t"}

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = [word for word in re.split("[ \t]+", test.args[0]) if word]
	if not words:
		return "\n"
	gap = GAPS[params["gap"]]
	line = gap.join(words)
	if params["ends"] == "around":
		line = gap + line + gap
	return line + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase(("   ",))]
	for text in ["  a  bc d ", "alone", "\tsee\t\tyou   soon\t", "1 2 3"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		words = ["".join(rng.choice("abXY12") for _ in range(rng.randint(1, 5)))
			for _ in range(rng.randint(1, 5))]
		tests.append(TestCase((rng.choice([" ", "  ", "\t"]).join(words) + rng.choice(["", " \t"]),)))
	return tests

EXERCISE = Exercise(
	name="word_spread",
	language="c",
	kind="program",
	assignment_name="spread_${gap}_${ends}",
	expected_files=("spread_${gap}_${ends}.c",),
	allowed_functions=("write",),
	themes=("space_spread",),
	params=(
		Param("gap", ("2", "4", "tab"), {
			"2": "two spaces",
			"4": "four spaces",
			"tab": "one tab",
		}),
		Param("ends", ("inside", "around"), {
			"inside": "The gap is only between the words: nothing before the first one or\n"
				"after the last one",
			"around": "The gap is also before the first word and after the last one",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays its words, in their\n"
		"order, separated by\n"
		"$gap,\n"
		"followed by a newline.\n"
		"$ends.\n"
		"\n"
		"A word is a part of the string between spaces or tabs, or the start or the\n"
		"end of the string.\n"
		"\n"
		"If the number of arguments is not 1, or if there is no word, the program\n"
		"displays only a newline."
	),
	examples=(
		TestCase(("  see  you   soon ",)),
		TestCase(("alone",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
