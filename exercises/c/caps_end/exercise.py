"""caps_end: an original program model in the style of "capitalize the words".

The program displays each of its arguments on its own line, with, in each
word, the last two letters, the last but one or the last vowel in uppercase; the other letters are put in lowercase or stay
as they are. The last letter of each word, a real 42 subject, is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase

VOWELS = "aeiouAEIOU"

def places(word, which):
	"""The indexes of the characters of `word` to put in uppercase."""
	if which == "first_two":
		return {0, 1}
	if which == "second":
		return {1}
	if which == "last_two":
		return {len(word) - 1, len(word) - 2}
	if which == "second_last":
		return {len(word) - 2} if len(word) >= 2 else set()
	vowels = [i for i, char in enumerate(word) if char in VOWELS]
	if not vowels:
		return set()
	return {vowels[0]} if which == "first_vowel" else {vowels[-1]}

def changed(word, which, rest):
	"""`word` with the letters of `which` in uppercase, the others by `rest`."""
	chosen = places(word, which)
	result = ""
	for i, char in enumerate(word):
		if i in chosen and "a" <= char <= "z":
			char = char.upper()
		elif i not in chosen and rest == "lower" and "A" <= char <= "Z":
			char = char.lower()
		result += char
	return result

def line(text, which, rest):
	"""One argument, each word changed, the spaces and tabs kept."""
	return re.sub(r"[^ \t]+", lambda match: changed(match.group(), which, rest), text)

def oracle(params, test):
	"""Return what the program must print: one line per argument."""
	if not test.args:
		return "\n"
	return "".join(line(text, params["which"], params["rest"]) + "\n" for text in test.args)

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed arguments, then random ones."""
	tests = [TestCase(()), TestCase(("",))]
	for args in [("hELLO wORLD a",), ("abc DEF x",), ("hello WORLD sky queue",),
			("  two\tspaces  ", "and ONE MORE"), ("42 is the answer!",)]:
		tests.append(TestCase(args))
	for _ in range(8):
		words = ["".join(rng.choice("aeiOUbcXYZ2") for _ in range(rng.randint(1, 6)))
			for _ in range(rng.randint(1, 4))]
		tests.append(TestCase((rng.choice([" ", "  ", "\t"]).join(words),)))
	return tests

REST = Param("rest", ("lower", "keep"), {
	"lower": "Every other letter is put in lowercase",
	"keep": "Every other letter stays as it is",
})

SUBJECT = (
	"Write a program that takes any number of strings and displays each one on\n"
	"its own line, with, in each word,\n"
	"$which\n"
	"in uppercase (if it is a letter).\n"
	"$rest.\n"
	"\n"
	"A word is a part of a string between spaces or tabs, or the start or the\n"
	"end of the string. The spaces and tabs are displayed as they are.\n"
	"\n"
	"If there is no argument, the program displays only a newline."
)

EXERCISE = Exercise(
	name="caps_end",
	language="c",
	kind="program",
	assignment_name="upper_${which}_${rest}",
	expected_files=("upper_${which}_${rest}.c",),
	allowed_functions=("write",),
	themes=("capitalize_last",),
	params=(
		Param("which", ("last_two", "second_last", "last_vowel"), {
			"last_two": "its last two characters",
			"second_last": "its last character but one",
			"last_vowel": "its last vowel (a, e, i, o, u, in either case)",
		}),
		REST,
	),
	subject=SUBJECT,
	examples=(
		TestCase(("hello WORLD queue", "a")),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
