"""set_run: an original function model in the style of "measure a run of
characters taken from a set".

The student writes a function that takes a string s and a set of
characters, given as a second string, and measures the characters of s that
are in the set: the run at the end of s, the longest run, the first run, or
all of them. The run at the start of s, a real 42 subject, is not one of
the kinds.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def runs(text, chars):
	"""Return the lengths of the runs of characters of chars in text, in order."""
	lengths = []
	current = 0
	for char in text:
		if char in chars:
			current += 1
		elif current:
			lengths.append(current)
			current = 0
	if current:
		lengths.append(current)
	return lengths

def measure(text, chars, kind):
	if kind == "end":
		count = 0
		while count < len(text) and text[len(text) - 1 - count] in chars:
			count += 1
		return count
	if kind == "count":
		return sum(char in chars for char in text)
	lengths = runs(text, chars)
	if kind == "longest":
		return max(lengths, default=0)
	return lengths[0] if lengths else 0

def oracle(params, test):
	"""Return what the test main prints: the size returned, then a newline."""
	return f"{measure(test.args[0], test.args[1], params['kind'])}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed pairs, then random ones."""
	pairs = [
		("aabxbba", "ab"), ("--12-345", "0123456789"), ("", "ab"), ("hello", ""),
		("xyz", "abc"), ("  hi  ", " "), ("aaaa", "a"), ("mississippi", "si"),
		("ab-ab-abab", "ba"), ("x", "x"),
	]
	for _ in range(8):
		text = "".join(rng.choice("abc-1 ") for _ in range(rng.randint(1, 14)))
		chars = "".join(rng.choice("abc-1 ") for _ in range(rng.randint(0, 3)))
		pairs.append((text, chars))
	return [TestCase(pair) for pair in pairs]

# The test main: av[1] is s, av[2] the set; it prints the size returned.
HARNESS = """#include <stdio.h>
#include <stddef.h>

size_t	ft_accept_${kind}(char *s, char *set);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%zu\\n", ft_accept_${kind}(av[1], av[2]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="set_run",
	language="c",
	kind="function",
	assignment_name="ft_accept_${kind}",
	expected_files=("ft_accept_${kind}.c",),
	allowed_functions=(),
	themes=("accept_span",),
	params=(
		Param("kind", ("end", "longest", "first", "count"), {
			"end": "how many characters of set there are in a row at the end of s: from\n"
				"its last character back, up to the first one that is not in set",
			"longest": "the length of the longest run of s made only of characters of set\n"
				"(a run is a group of characters next to each other)",
			"first": "the length of the first run of s made only of characters of set: the\n"
				"characters before it, which are not in set, are skipped",
			"count": "how many characters of s are in set, wherever they are in s",
		}),
	),
	subject=(
		"Write a function that takes a string s and a string set, and returns\n"
		"$kind.\n"
		"\n"
		"A character is in set if it appears in it at least once. The order of the\n"
		"characters of set does not matter, and set may be empty.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"size_t\t$assignment(char *s, char *set);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])}, {c_string(test.args[1])})",
	examples=(TestCase(("aabxbba", "ab")), TestCase(("--12-345", "0123456789")),
		TestCase(("hello", ""))),
)
