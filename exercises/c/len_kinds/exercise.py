"""len_kinds: an original function model in the style of "measure a string".

The student writes a function that measures a string another way than its
length: its number of words, its longest word, its characters that are not
blanks, or its characters before the first digit. The length of the whole
string, the real 42 subject, is not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def measure(text, what):
	words = re.findall(r"[^ \t]+", text)
	if what == "words":
		return len(words)
	if what == "longest_word":
		return max(map(len, words), default=0)
	if what == "no_spaces":
		return sum(len(word) for word in words)
	digit = re.search(r"[0-9]", text)
	return digit.start() if digit else len(text)

def oracle(params, test):
	"""Return what the test main prints: the int returned, then a newline."""
	return f"{measure(test.args[0], params['what'])}\n"

def generate_tests(params, rng):
	texts = ["", "  hello big world ", "ab3cd", "one", "\t tab\tand  spaces\t", "42 is it", "no digit here",
		"     ", "a b c d e"]
	for _ in range(8):
		texts.append("".join(rng.choice("ab 9\tXYz") for _ in range(rng.randint(1, 16))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; it prints the int returned.
HARNESS = """#include <stdio.h>

int	ft_len_${what}(char *str);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\\n", ft_len_${what}(av[1]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="len_kinds",
	language="c",
	kind="function",
	assignment_name="ft_len_${what}",
	expected_files=("ft_len_${what}.c",),
	allowed_functions=(),
	themes=("string_length",),
	params=(
		Param("what", ("words", "longest_word", "no_spaces", "until_digit"), {
			"words": "its number of words",
			"longest_word": "the length of its longest word (0 if it has no word)",
			"no_spaces": "its number of characters that are not spaces nor tabs",
			"until_digit": "its number of characters before its first digit (its whole length if\n"
				"it has no digit)",
		}),
	),
	subject=(
		"Write a function that takes a string and returns\n"
		"$what.\n"
		"\n"
		"A word is a group of characters that are not spaces nor tabs, as long as it\n"
		"can be. An empty string gives 0.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("  hello big world ",)), TestCase(("ab3cd",)), TestCase(("",))),
)
