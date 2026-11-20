"""rev_part: an original program model in the style of "display a string backwards".

The program turns around a part of a string: the letters of each word, the
letters only, the two halves, each pair of characters, or the characters at
even places. The whole string backwards, a real 42 subject, is not one of
the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase

def turned(text, part):
	"""`text` with the part of the variant turned around."""
	if part == "each_word":
		return re.sub(r"[^ \t]+", lambda word: word.group()[::-1], text)
	if part == "letters_only":
		letters = [char for char in text if char.isascii() and char.isalpha()][::-1]
		return "".join(letters.pop(0) if char.isascii() and char.isalpha() else char
			for char in text)
	if part == "halves":
		middle = len(text) // 2
		return text[middle:] + text[:middle]
	if part == "pairs":
		chars = list(text)
		for i in range(0, len(chars) - 1, 2):
			chars[i], chars[i + 1] = chars[i + 1], chars[i]
		return "".join(chars)
	chars = list(text)
	chars[0::2] = chars[0::2][::-1]
	return "".join(chars)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	return turned(test.args[0], params["part"]) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase(("x",))]
	for text in ["  hello  big world ", "a-bc!d", "abcdef", "abcdefg", "zaz", "42 is\tthe answer"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		tests.append(TestCase(("".join(rng.choice("abcXYZ 1-\t") for _ in range(rng.randint(1, 15))),)))
	return tests

EXERCISE = Exercise(
	name="rev_part",
	language="c",
	kind="program",
	assignment_name="rev_${part}",
	expected_files=("rev_${part}.c",),
	allowed_functions=("write",),
	themes=("reverse_print",),
	params=(
		Param("part", ("each_word", "letters_only", "halves", "pairs", "odd_places"), {
			"each_word": "the characters of each word in reverse order, each word staying in\n"
				"its place (words are cut by spaces and tabs, which stay as they are)",
			"letters_only": "its letters in reverse order, every other character staying in its\n"
				"place",
			"halves": "its two halves swapped: the second half first, then the first half\n"
				"(with an odd length, the middle character goes with the second half)",
			"pairs": "each pair of characters swapped: the first with the second, the third\n"
				"with the fourth and so on (a last character alone stays in its place)",
			"odd_places": "the characters at places 0, 2, 4 and so on in reverse order among\n"
				"themselves, the others staying in their places",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays it, followed by a\n"
		"newline, with\n"
		"$part.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	examples=(
		TestCase(("  hello  big world ",)),
		TestCase(("abcdefg",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
