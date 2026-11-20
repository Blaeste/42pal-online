"""word_pick: an original program model on the theme "the words of a string".

The program takes one string and displays one of its words (the first, the
second, the last or the longest one) as it is, in uppercase or reversed.
The first word and the last word as they are give back two real 42
subjects: both are left out.
"""

import re

from pal42.model import Exercise, Param, TestCase

LOWERCASE_TO_UPPERCASE = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def pick(words, which):
	"""The word `which` asks for, or None if there is none."""
	if which == "first":
		return words[0]
	if which == "second":
		return words[1] if len(words) > 1 else None
	if which == "last":
		return words[-1]
	# max() keeps the first of the longest words.
	return max(words, key=len)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	# Words are separated by spaces and tabs only.
	words = [word for word in re.split("[ \t]+", test.args[0]) if word]
	word = pick(words, params["which"]) if words else None
	if word is None:
		return "\n"
	if params["how"] == "upper":
		word = word.translate(LOWERCASE_TO_UPPERCASE)
	elif params["how"] == "reversed":
		word = word[::-1]
	return word + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random strings."""
	tests = [
		TestCase(()),
		TestCase(("two", "args")),
		TestCase(("",)),
		TestCase((" \t ",)),
		TestCase(("alone",)),
		TestCase(("  lorem\tipsum  dolor ",)),
		TestCase(("a bb ccc dd e",)),
		TestCase(("Tie tie abc",)),
		TestCase(("x2-Go! now",)),
	]
	for _ in range(10):
		words = [
			"".join(rng.choice("abcdefghijKLMNOP0123-!?") for _ in range(rng.randint(1, 8)))
			for _ in range(rng.randint(1, 6))
		]
		blanks = [rng.choice([" ", "  ", "\t", " \t "]) for _ in range(len(words) + 1)]
		text = blanks[0] * rng.randint(0, 1)
		for word, blank in zip(words, blanks[1:]):
			text += word + blank
		if rng.randint(0, 1):
			text = text.rstrip(" \t")
		tests.append(TestCase((text,)))
	return tests

EXERCISE = Exercise(
	name="word_pick",
	language="c",
	kind="program",
	assignment_name="${which}_word_${how}",
	expected_files=("${which}_word_${how}.c",),
	allowed_functions=("write",),
	themes=("find_word",),
	params=(
		Param("which", ("first", "second", "last", "longest"), {
			"first": "its first word",
			"second": "its second word",
			"last": "its last word",
			"longest": "its longest word (the first of them if several are as long)",
		}),
		Param("how", ("plain", "upper", "reversed"), {
			"plain": "as it is",
			"upper": "with its lowercase letters turned into uppercase",
			"reversed": "with its characters in reverse order",
		}),
	),
	# first_word and last_word are real subjects.
	forbidden=(
		{"which": "first", "how": "plain"},
		{"which": "last", "how": "plain"},
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
	# No tab in the examples: typed in a terminal, a tab completes a file name.
	examples=(
		TestCase(("  lorem ipsum  dolor ",)),
		TestCase(("a bb ccc dd e",)),
		TestCase((" ",)),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
