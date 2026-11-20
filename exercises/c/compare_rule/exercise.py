"""compare_rule: an original function model in the style of "compare two strings".

The student writes a function that compares two strings with a rule:
letters in either case, from the end, the shorter one first, or without the
spaces and tabs; it returns the sign of the comparison or the difference
found. The plain comparison, a real 42 subject, is not one of the rules.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def first_difference(a, b):
	"""The difference of the first different characters (0 for a missing one), or 0."""
	for i in range(max(len(a), len(b))):
		x = ord(a[i]) if i < len(a) else 0
		y = ord(b[i]) if i < len(b) else 0
		if x != y:
			return x - y
	return 0

def compare(s1, s2, rule):
	"""The difference that the rule finds between s1 and s2."""
	if rule == "any_case":
		return first_difference(s1.lower(), s2.lower())
	if rule == "from_end":
		return first_difference(s1[::-1], s2[::-1])
	if rule == "length_first":
		return len(s1) - len(s2) if len(s1) != len(s2) else first_difference(s1, s2)
	spaceless = lambda text: text.replace(" ", "").replace("\t", "")
	return first_difference(spaceless(s1), spaceless(s2))

def oracle(params, test):
	"""Return what the test main prints: the int returned, then a newline."""
	difference = compare(test.args[0], test.args[1], params["rule"])
	if params["result"] == "sign":
		difference = (difference > 0) - (difference < 0)
	return f"{difference}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed pairs, then random ones."""
	pairs = [("", ""), ("a", ""), ("", "a"), ("HELLO", "hello"), ("Abc", "ABD"), ("xab", "yab"),
		("ab", "b"), ("zz", "aaa"), ("abc", "abd"), ("a b\tc", "abc"), ("ab", " a c"), ("same", "same")]
	for _ in range(8):
		pairs.append(tuple("".join(rng.choice("aAbB c\t") for _ in range(rng.randint(0, 6)))
			for _ in range(2)))
	return [TestCase(pair) for pair in pairs]

# The test main: av[1] and av[2] are the two strings; it prints what is returned.
HARNESS = """#include <stdio.h>

int	ft_compare_${rule}_${result}(char *s1, char *s2);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\\n", ft_compare_${rule}_${result}(av[1], av[2]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="compare_rule",
	language="c",
	kind="function",
	assignment_name="ft_compare_${rule}_${result}",
	expected_files=("ft_compare_${rule}_${result}.c",),
	allowed_functions=(),
	themes=("string_compare",),
	params=(
		Param("rule", ("any_case", "from_end", "length_first", "skip_spaces"), {
			"any_case": "character by character from the start, a letter and its other case\n"
				"being the same (each letter is taken in lowercase)",
			"from_end": "character by character from their last characters back to their\n"
				"first ones; past the start of the shorter string, its character is 0",
			"length_first": "by their lengths first: the difference is the length of s1 minus\n"
				"the length of s2; only as long, they are compared character by\n"
				"character from the start",
			"skip_spaces": "character by character from the start, as if their spaces and tabs\n"
				"were not there",
		}),
		Param("result", ("sign", "difference"), {
			"sign": "-1 if s1 comes first, 1 if s2 comes first, and 0 if they are the same",
			"difference": "the difference found: the first character of s1 that differs minus\n"
				"the one of s2 at the same place (0 past the end of a string), or 0",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that compares the strings s1 and s2\n"
		"$rule.\n"
		"It returns\n"
		"$result.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char *s1, char *s2);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])}, {c_string(test.args[1])})",
	examples=(TestCase(("Abc", "ABD")), TestCase(("ab", "b")), TestCase(("a b", "ab"))),
)
