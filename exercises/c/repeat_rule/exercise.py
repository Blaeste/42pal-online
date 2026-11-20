"""repeat_rule: an original program model in the style of "repeat each letter".

The program displays each character of a string several times: each letter
by its rank from the end of the alphabet, each digit by its value, each
character by its place, each character of a word by the number of its word,
or each vowel by its rank among the vowels. Each letter by its rank in the
alphabet, a real 42 subject, is not one of the rules.
"""

import re

from pal42.model import Exercise, Param, TestCase

def times(rule, char, place, word):
	"""How many times `char` is displayed: place counts from 1, word too (0 for a blank)."""
	lower = char.lower() if char.isascii() else char
	if rule == "reverse_rank":
		return 26 - (ord(lower) - ord("a")) if "a" <= lower <= "z" else 1
	if rule == "digit_value":
		return int(char) if "0" <= char <= "9" else 1
	if rule == "position":
		return place
	if rule == "word_number":
		return word or 1
	return "aeiou".index(lower) + 1 if lower in "aeiou" and lower else 1

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	text = test.args[0]
	# The number of the word of each character (0 for spaces and tabs).
	words = [0] * len(text)
	for number, match in enumerate(re.finditer(r"[^ \t]+", text), start=1):
		for i in range(match.start(), match.end()):
			words[i] = number
	return "".join(char * times(params["rule"], char, i + 1, words[i])
		for i, char in enumerate(text)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random short ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",))]
	for text in ["zyA", "Hello", "a3b0c1", "a b", "hi you  all", "abc", "Zz 9\tok!"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		tests.append(TestCase(("".join(rng.choice("aeuxyzBO 2-7") for _ in range(rng.randint(1, 8))),)))
	return tests

EXERCISE = Exercise(
	name="repeat_rule",
	language="c",
	kind="program",
	assignment_name="repeat_by_${rule}",
	expected_files=("repeat_by_${rule}.c",),
	allowed_functions=("write",),
	themes=("letter_repeat",),
	params=(
		Param("rule", ("reverse_rank", "digit_value", "position", "word_number", "vowel_rank"), {
			"reverse_rank": "each letter by its rank from the end of the alphabet: z once, y\n"
				"twice and so on, a 26 times, whatever its case; every other character\n"
				"once",
			"digit_value": "each digit as many times as its value: 3 three times, 0 not at all;\n"
				"every other character once",
			"position": "each character as many times as its place in the string: the first\n"
				"one once, the second one twice and so on",
			"word_number": "each character of a word as many times as the number of its word (the\n"
				"first word once, the second word twice, and so on). The words are cut by\n"
				"spaces and tabs, which are displayed once",
			"vowel_rank": "each vowel by its rank among the vowels: a once, e twice, i 3 times,\n"
				"o 4 times and u 5 times, whatever its case; every other character once",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays it, followed by a\n"
		"newline, with each character repeated by this rule:\n"
		"$rule.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	# Short examples: each letter near a would be displayed about 26 times.
	examples=(
		TestCase(("zyx 2",)),
		TestCase(("ou 9",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
