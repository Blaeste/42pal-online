"""rev_inplace: an original function model in the style of "reverse a string in place".

The student writes a function that turns around a part of a string, in
place, and returns the string: the letters of each word, the letters only,
the two halves, or all but the first and last characters. The whole string
turned around, a real 42 subject, is not one of the parts.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def turned(text, part):
	if part == "each_word":
		return re.sub(r"[^ \t]+", lambda word: word.group()[::-1], text)
	if part == "letters_only":
		letters = [char for char in text if char.isascii() and char.isalpha()][::-1]
		return "".join(letters.pop(0) if char.isascii() and char.isalpha() else char for char in text)
	if part == "halves":
		middle = len(text) // 2
		return text[middle:] + text[:middle]
	return text if len(text) <= 2 else text[0] + text[-2:0:-1] + text[-1]

def oracle(params, test):
	"""Return what the test main prints: the string after the call, then a newline."""
	return turned(test.args[0], params["part"]) + "\n"

def generate_tests(params, rng):
	texts = ["", "x", "ab", "hello big world", "a-bc!d", "abcdefg", "  two  spaces "]
	for _ in range(8):
		texts.append("".join(rng.choice("abcXY 1-") for _ in range(rng.randint(1, 15))))
	return [TestCase((text,)) for text in texts]

# The test main: copies av[1], calls the function, then prints the string;
# it says so if the function returns another pointer than the string.
HARNESS = """#include <stdio.h>
#include <string.h>

char	*ft_rev_${part}(char *str);

int	main(int ac, char **av)
{
	char	text[1024];

	(void)ac;
	strcpy(text, av[1]);
	if (ft_rev_${part}(text) != text)
		printf("(the pointer returned is not str) ");
	printf("%s\\n", text);
	return (0);
}
"""

EXERCISE = Exercise(
	name="rev_inplace",
	language="c",
	kind="function",
	assignment_name="ft_rev_${part}",
	expected_files=("ft_rev_${part}.c",),
	allowed_functions=(),
	themes=("string_reverse",),
	params=(
		Param("part", ("each_word", "letters_only", "halves", "inner"), {
			"each_word": "the characters of each word in reverse order, each word staying in its\n"
				"place (words are cut by spaces and tabs)",
			"letters_only": "its letters in reverse order, every other character staying in its\n"
				"place",
			"halves": "its two halves swapped: the second half first, then the first one\n"
				"(with an odd length, the middle character goes with the second half)",
			"inner": "all its characters in reverse order but the first one and the last\n"
				"one, which stay in their places",
		}),
	),
	subject=(
		"Write a function that changes the string str, in place, so that it holds\n"
		"$part,\n"
		"and returns str.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *str);\n"
		"\n"
		"In the examples, the line below each call shows str after the call."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("hello big world",)), TestCase(("abcdefg",))),
)
