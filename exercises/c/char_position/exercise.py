"""char_position: an original function model on the theme "go through a string".

The student writes one function that looks for a character in a string:
how many times it appears, or the index of its first or last appearance.
The variants also change whether the case of letters matters.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_char, c_string

def oracle(params, test):
	"""Return what the test main prints: the function's result, then a newline."""
	text, char = test.args
	# Any case: compare everything in lowercase (the tests use ASCII only).
	if params["case"] == "any":
		text, char = text.lower(), char.lower()
	if params["mode"] == "count":
		return f"{text.count(char)}\n"
	# find and rfind give the first and last index, or -1 when char is absent.
	if params["mode"] == "first":
		return f"{text.find(char)}\n"
	return f"{text.rfind(char)}\n"

# Letters of both cases, so that "exact" and "any" give different results.
ALPHABET = "abcABC hello HELLO"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random ones.

	Each test is (str, c), c being one character: the test main reads av[2][0].
	The same rng (same seed) gives the same tests, for every variant.
	"""
	tests = [
		# Empty string, c alone, c everywhere, c absent, c at both ends.
		TestCase(("", "a")),
		TestCase(("a", "a")),
		TestCase(("aaa", "a")),
		TestCase(("abc", "z")),
		TestCase(("abca", "a")),
		# Only the case differs: exact and any disagree here.
		TestCase(("Hello", "h")),
		TestCase(("HELLO", "l")),
		TestCase(("hello world", "o")),
	]
	for _ in range(10):
		text = "".join(rng.choice(ALPHABET) for _ in range(rng.randint(0, 20)))
		tests.append(TestCase((text, rng.choice(ALPHABET))))
	return tests

# The test main: av[1] is str, av[2][0] is c; it prints what the function returns.
HARNESS = """#include <stdio.h>

int	ft_char_${mode}(char *str, char c);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\\n", ft_char_${mode}(av[1], av[2][0]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="char_position",
	language="c",
	kind="function",
	assignment_name="ft_char_${mode}",
	expected_files=("ft_char_${mode}.c",),
	allowed_functions=(),
	themes=("string_length",),
	params=(
		Param("mode", ("count", "first", "last"), {
			"count": "how many times the character c appears in the string str",
			"first": "the index of the first c in the string str, or -1 if there is none",
			"last": "the index of the last c in the string str, or -1 if there is none",
		}),
		Param("case", ("exact", "any"), {
			"exact": "exactly: 'a' and 'A' are different",
			"any": "without case: 'a' and 'A' are the same letter",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns\n"
		"$mode.\n"
		"Letters are compared $case.\n"
		"The first character of str has the index 0.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char *str, char c);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	# A test is (str, c): written as the call ft_char_count("hello", 'l').
	call=lambda name, test: f"{name}({c_string(test.args[0])}, {c_char(test.args[1])})",
	examples=(
		TestCase(("hello world", "o")),
		TestCase(("Hello", "h")),
		TestCase(("", "a")),
	),
)
