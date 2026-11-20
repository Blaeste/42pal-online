"""word_order: an original program model on the theme "reorder the words of a string".

The program takes one string and displays its words in another order:
reversed, rotated one way or the other, sorted, or by length, with one of
three separators. Reversed or rotated left, with one space, give back two
real exam subjects of this theme: forbidden.
"""

import re

from pal42.model import Exercise, Param, TestCase

# What the words are separated by, in the output.
SEPARATORS = {"space": " ", "newline": "\n", "comma": ", "}

def reorder(words, order):
	"""Return `words` in the order the variant asks for."""
	if order == "reverse":
		return words[::-1]
	if order == "rotate_left":
		return words[1:] + words[:1]
	if order == "rotate_right":
		return words[-1:] + words[:-1]
	if order == "sort":
		return sorted(words)
	# sorted is stable: words as long keep their order.
	return sorted(words, key=len)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = [word for word in re.split("[ \t]+", test.args[0]) if word]
	return SEPARATORS[params["separator"]].join(reorder(words, params["order"])) + "\n"

# Letters of both cases and digits for the words; spaces and tabs between.
LETTERS = "abcABC0189"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random ones."""
	tests = [
		TestCase(()),
		TestCase(("two", "args")),
		TestCase(("",)),
		TestCase((" \t ",)),
		TestCase(("solo",)),
		TestCase(("  one two\tthree  ",)),
		TestCase(("bb a ccc dd",)),
		TestCase(("Zebra apple Mango",)),
	]
	for _ in range(10):
		words = [
			"".join(rng.choice(LETTERS) for _ in range(rng.randint(1, 6)))
			for _ in range(rng.randint(1, 6))
		]
		gaps = [rng.choice([" ", "  ", "\t", " \t"]) for _ in words]
		text = rng.choice(["", " "]) + "".join(word + gap for word, gap in zip(words, gaps))
		tests.append(TestCase((text,)))
	return tests

EXERCISE = Exercise(
	name="word_order",
	language="c",
	kind="program",
	assignment_name="${order}_words_${separator}",
	expected_files=("${order}_words_${separator}.c",),
	allowed_functions=("write",),
	themes=("word_reverse",),
	params=(
		Param("order", ("reverse", "rotate_left", "rotate_right", "sort", "by_length"), {
			"reverse": "from the last one to the first one",
			"rotate_left": "from the second one, the first one moved to the end",
			"rotate_right": "the last one first, then the others in their order",
			"sort": "sorted in ASCII order",
			"by_length": "from the shortest to the longest (in their order if as long)",
		}),
		Param("separator", ("space", "newline", "comma"), {
			"space": "one space",
			"newline": "a newline (one word per line)",
			"comma": "a comma and a space",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays its words\n"
		"$order,\n"
		"separated by\n"
		"$separator, then a newline.\n"
		"A word is a run of characters other than spaces and tabs.\n"
		"\n"
		"If the number of arguments is not 1, or if the string has no word, it\n"
		"displays only a newline."
	),
	examples=(
		TestCase(("  the quick\tbrown fox ",)),
		TestCase(("solo",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
	# Reversed or rotated left with one space: two real exam subjects.
	forbidden=(
		{"order": "reverse", "separator": "space"},
		{"order": "rotate_left", "separator": "space"},
	),
)
