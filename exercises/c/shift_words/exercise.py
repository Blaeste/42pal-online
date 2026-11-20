"""shift_words: an original function model in the style of "shift letters in
the alphabet".

The student writes a function that shifts, in place, the letters of a string
by a number that changes: the rank of their word, their own rank among the
letters, or the length of their word. One shift for every letter, the real
42 subjects, is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def shift(char, steps):
	for first in "aA":
		if first <= char <= chr(ord(first) + 25):
			return chr(ord(first) + (ord(char) - ord(first) + steps) % 26)
	return char

def oracle(params, test):
	"""Return what the test main prints: the string after the call, then a newline."""
	text, by = test.args[0], params["by"]
	steps = [0] * len(text)
	if by == "position":
		count = 0
		for index, char in enumerate(text):
			if char.isascii() and char.isalpha():
				count += 1
				steps[index] = count
	else:
		for rank, word in enumerate(re.finditer(r"[^ \t]+", text), start=1):
			for index in range(word.start(), word.end()):
				steps[index] = rank if by == "word_rank" else word.end() - word.start()
	return "".join(shift(char, step) for char, step in zip(text, steps)) + "\n"

def generate_tests(params, rng):
	texts = ["", "ab yz Az", "abc a", "hi abc", "a1 Z", "zzz zzz zzz", "  Two  words ", "x", "A-b c"]
	for _ in range(8):
		texts.append("".join(rng.choice("azAZm 1") for _ in range(rng.randint(1, 16))))
	return [TestCase((text,)) for text in texts]

# The test main: copies av[1], calls the function, then prints the string;
# it says so if the function returns another pointer than the string.
HARNESS = """#include <stdio.h>
#include <string.h>

char	*ft_rot_${by}(char *str);

int	main(int ac, char **av)
{
	char	text[1024];

	(void)ac;
	strcpy(text, av[1]);
	if (ft_rot_${by}(text) != text)
		printf("(the pointer returned is not str) ");
	printf("%s\\n", text);
	return (0);
}
"""

EXERCISE = Exercise(
	name="shift_words",
	language="c",
	kind="function",
	assignment_name="ft_rot_${by}",
	expected_files=("ft_rot_${by}.c",),
	allowed_functions=(),
	themes=("letter_rotation",),
	params=(
		Param("by", ("word_rank", "position", "word_length"), {
			"word_rank": "the rank of its word: the letters of the first word by 1, those of the\n"
				"second word by 2, and so on",
			"position": "its rank among the letters of the string: the first letter by 1, the\n"
				"second letter by 2, and so on (the other characters are not counted)",
			"word_length": "the length of its word, in characters (a1 is a word of 2 characters)",
		}),
	),
	subject=(
		"Write a function that shifts, in place, each letter of the string str\n"
		"forward in the alphabet by\n"
		"$by.\n"
		"A letter keeps its case and goes round: z shifted by 1 gives a, and Z gives\n"
		"A. The other characters do not change. A word is a group of characters that\n"
		"are not spaces nor tabs. The function returns str.\n"
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
		"word_rank": (TestCase(("ab yz Az",)),),
		"position": (TestCase(("abc a",)),),
		"word_length": (TestCase(("hi abc",)), TestCase(("a1 Z",))),
	}[params["by"]],
)
