"""set_find: an original function model in the style of "find in a string a
character of a set".

The student writes a function that takes a string s and a set of
characters, given as a second string, and returns a pointer into s: to the
last character in the set, to the first or the last one out of it, or to
the first two characters of the set in a row. The first character in the
set, a real 42 subject, is not one of the kinds.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def found(text, chars, kind):
	"""Return the index of the character the function points to, or None."""
	indexes = range(len(text))
	if kind == "last":
		matches = [i for i in indexes if text[i] in chars][-1:]
	elif kind == "first_out":
		matches = [i for i in indexes if text[i] not in chars][:1]
	elif kind == "last_out":
		matches = [i for i in indexes if text[i] not in chars][-1:]
	else:
		matches = [i for i in indexes[:-1] if text[i] in chars and text[i + 1] in chars][:1]
	return matches[0] if matches else None

def oracle(params, test):
	"""Return what the test main prints: NULL, or the index then the rest of s."""
	text = test.args[0]
	index = found(text, test.args[1], params["kind"])
	return "NULL\n" if index is None else f"{index}: {text[index:]}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed pairs, then random ones."""
	pairs = [
		("hello world", "ow"), ("aaab", "a"), ("abc", "xyz"), ("", "a"), ("aaa", "a"),
		("hello", ""), ("a1b22c", "0123456789"), ("  x  ", " "), ("xyxy", "yx"),
	]
	for _ in range(8):
		text = "".join(rng.choice("abc- ") for _ in range(rng.randint(1, 14)))
		chars = "".join(rng.choice("abc- ") for _ in range(rng.randint(0, 3)))
		pairs.append((text, chars))
	return [TestCase(pair) for pair in pairs]

# The test main: av[1] is s, av[2] the set. It prints NULL, or where the
# pointer returned is in s, then the string from there.
HARNESS = """#include <stdio.h>

char	*ft_find_${kind}(char *s, char *set);

int	main(int ac, char **av)
{
	char	*found;

	(void)ac;
	found = ft_find_${kind}(av[1], av[2]);
	if (found == NULL)
		printf("NULL\\n");
	else
		printf("%ld: %s\\n", (long)(found - av[1]), found);
	return (0);
}
"""

EXERCISE = Exercise(
	name="set_find",
	language="c",
	kind="function",
	assignment_name="ft_find_${kind}",
	expected_files=("ft_find_${kind}.c",),
	allowed_functions=(),
	themes=("set_search",),
	params=(
		Param("kind", ("last", "first_out", "last_out", "pair"), {
			"last": "the last character of s that is in set",
			"first_out": "the first character of s that is not in set",
			"last_out": "the last character of s that is not in set",
			"pair": "the first character of s that is in set and is followed by another\n"
				"character of set: the first of two characters of set in a row",
		}),
	),
	subject=(
		"Write a function that takes a string s and a string set, and returns a\n"
		"pointer to\n"
		"$kind.\n"
		"If there is no such character in s, it returns NULL.\n"
		"\n"
		"A character is in set if it appears in it at least once. The order of the\n"
		"characters of set does not matter, and set may be empty. The terminating\n"
		"'\\0' of s is never one of its characters.\n"
		"\n"
		"In the examples, the test main prints where the pointer returned is in s,\n"
		"then the string from there.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *s, char *set);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])}, {c_string(test.args[1])})",
	examples=(TestCase(("hello world", "ow")), TestCase(("aaab", "a")), TestCase(("abc", "xyz"))),
)
