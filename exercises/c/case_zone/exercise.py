"""case_zone: an original function model in the style of "swap the case of letters".

The student writes a function that swaps, in place, the case of the letters
of one zone of a string: its first half, its words of odd rank, the letters
right after a digit, or the letters between brackets. Swapping the case of
every letter, the real 42 subject, is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def in_zone(text, zone):
	"""For each character of text, True if it is in the zone."""
	if zone == "first_half":
		return [index < len(text) // 2 for index in range(len(text))]
	if zone == "after_digit":
		return [index > 0 and text[index - 1].isdigit() for index in range(len(text))]
	if zone == "odd_words":
		marks = [False] * len(text)
		for rank, word in enumerate(re.finditer(r"[^ \t]+", text)):
			if rank % 2 == 0:
				marks[word.start():word.end()] = [True] * (word.end() - word.start())
		return marks
	marks, inside = [], False
	for char in text:
		if char == "(":
			inside = True
		elif char == ")":
			inside = False
		marks.append(inside)
	return marks

def oracle(params, test):
	"""Return what the test main prints: the string after the call, then a newline."""
	text = test.args[0]
	return "".join(char.swapcase() if mark and char.isascii() and char.isalpha() else char
		for char, mark in zip(text, in_zone(text, params["zone"]))) + "\n"

def generate_tests(params, rng):
	texts = ["", "Hello World", "one Two three FOUR", "a1b2Cd", "ab(cD)Ef(g", "x", "  lead  Space ", "(())", "9Zz9"]
	for _ in range(8):
		texts.append("".join(rng.choice("aBc ()1Z") for _ in range(rng.randint(1, 14))))
	return [TestCase((text,)) for text in texts]

# The test main: copies av[1], calls the function, then prints the string;
# it says so if the function returns another pointer than the string.
HARNESS = """#include <stdio.h>
#include <string.h>

char	*ft_swapcase_${zone}(char *str);

int	main(int ac, char **av)
{
	char	text[1024];

	(void)ac;
	strcpy(text, av[1]);
	if (ft_swapcase_${zone}(text) != text)
		printf("(the pointer returned is not str) ");
	printf("%s\\n", text);
	return (0);
}
"""

EXERCISE = Exercise(
	name="case_zone",
	language="c",
	kind="function",
	assignment_name="ft_swapcase_${zone}",
	expected_files=("ft_swapcase_${zone}.c",),
	allowed_functions=(),
	themes=("case_swap",),
	params=(
		Param("zone", ("first_half", "odd_words", "after_digit", "in_brackets"), {
			"first_half": "in the first half of the string: its first n / 2 characters, n being\n"
				"its length (the middle character of an odd length is not in it)",
			"odd_words": "in its words of odd rank: the first word, the third, the fifth, and so\n"
				"on (a word is a group of characters that are not spaces nor tabs)",
			"after_digit": "right after a digit: the letter that follows each digit",
			"in_brackets": "between brackets: after each ( up to the next ), or up to the end of\n"
				"the string if no ) comes",
		}),
	),
	subject=(
		"Write a function that swaps, in place, the case of the letters of the string\n"
		"str that are\n"
		"$zone.\n"
		"An uppercase letter becomes lowercase and a lowercase one uppercase; the\n"
		"other characters do not change. The function returns str.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *str);\n"
		"\n"
		"In the examples, the line below a call shows str after it."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=lambda params: {
		"first_half": (TestCase(("Hello World",)),),
		"odd_words": (TestCase(("one Two three FOUR",)),),
		"after_digit": (TestCase(("a1b2Cd",)),),
		"in_brackets": (TestCase(("ab(cD)Ef(g",)),),
	}[params["zone"]],
)
