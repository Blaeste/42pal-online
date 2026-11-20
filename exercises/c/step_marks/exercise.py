"""step_marks: an original function model in the style of "move each letter
one step in the alphabet".

The student writes a function that moves, in place, some letters of a
string to the next letter: the first letter of each word, the last one, or
the uppercase letters. Every letter to the next one, the real 42 subject,
is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def step(char):
	for first in "aA":
		if first <= char <= chr(ord(first) + 25):
			return chr(ord(first) + (ord(char) - ord(first) + 1) % 26)
	return char

def oracle(params, test):
	"""Return what the test main prints: the string after the call, then a newline."""
	text, where = test.args[0], params["where"]
	if where == "capitals":
		marked = {index for index, char in enumerate(text) if "A" <= char <= "Z"}
	else:
		words = list(re.finditer(r"[^ \t]+", text))
		marked = {word.start() if where == "word_starts" else word.end() - 1 for word in words}
	return "".join(step(char) if index in marked else char for index, char in enumerate(text)) + "\n"

def generate_tests(params, rng):
	texts = ["", "abc zed Yo 1x", "abc zed Yo x1", "Az Zz yY", "z", "  Z  ", "a1 b2 c3", "Hello World Zz"]
	for _ in range(8):
		texts.append("".join(rng.choice("azAZm 1") for _ in range(rng.randint(1, 16))))
	return [TestCase((text,)) for text in texts]

# The test main: copies av[1], calls the function, then prints the string;
# it says so if the function returns another pointer than the string.
HARNESS = """#include <stdio.h>
#include <string.h>

char	*ft_step_${where}(char *str);

int	main(int ac, char **av)
{
	char	text[1024];

	(void)ac;
	strcpy(text, av[1]);
	if (ft_step_${where}(text) != text)
		printf("(the pointer returned is not str) ");
	printf("%s\\n", text);
	return (0);
}
"""

EXERCISE = Exercise(
	name="step_marks",
	language="c",
	kind="function",
	assignment_name="ft_step_${where}",
	expected_files=("ft_step_${where}.c",),
	allowed_functions=(),
	themes=("letter_step",),
	params=(
		Param("where", ("word_starts", "word_ends", "capitals"), {
			"word_starts": "the first character of each word, when it is a letter",
			"word_ends": "the last character of each word, when it is a letter",
			"capitals": "each uppercase letter",
		}),
	),
	subject=(
		"Write a function that replaces, in place, in the string str\n"
		"$where\n"
		"by the next letter of the alphabet: a becomes b, and z becomes a; the\n"
		"letter keeps its case (Z becomes A). The other characters do not change. A\n"
		"word is a group of characters that are not spaces nor tabs. The function\n"
		"returns str.\n"
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
		"word_starts": (TestCase(("abc zed Yo 1x",)),),
		"word_ends": (TestCase(("abc zed Yo x1",)),),
		"capitals": (TestCase(("Az Zz yY",)),),
	}[params["where"]],
)
