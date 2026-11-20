"""replace_count: an original function model in the style of "replace a character".

The student writes a function that replaces, in place, a character by
another one only at some places of a string (at the start of words, at
their end, in runs of two or more, or anywhere but the two ends) and
returns how many it replaced. Replacing every occurrence, the real 42
subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_char, c_string

def at_place(text, index, where):
	blank = lambda i: i < 0 or i >= len(text) or text[i] in " \t"
	if where == "word_start":
		return blank(index - 1)
	if where == "word_end":
		return blank(index + 1)
	if where == "in_runs":
		return text[index - 1:index] == text[index] or text[index + 1:index + 2] == text[index]
	return 0 < index < len(text) - 1

def oracle(params, test):
	"""Return what the test main prints: the count, a space, the string after the call."""
	text, old, new = test.args[0], test.args[1], test.args[2]
	places = [index for index, char in enumerate(text) if char == old and at_place(text, index, params["where"])]
	result = "".join(new if index in places else char for index, char in enumerate(text))
	return f"{len(places)} {result}\n"

def generate_tests(params, rng):
	triples = [("banana band", "b", "B"), ("banana band", "a", "A"), ("aabaaa x a", "a", "-"), ("aaa", "a", "b"),
		("aXa", "a", "b"), ("", "a", "b"), ("no match", "z", "y"), ("a", "a", "b"), (" aa a ", "a", "*")]
	for _ in range(8):
		text = "".join(rng.choice("aab -x") for _ in range(rng.randint(1, 14)))
		triples.append((text, rng.choice("ab"), rng.choice("XY")))
	return [TestCase(triple) for triple in triples]

# The test main: copies av[1], calls the function with av[2][0] and av[3][0],
# then prints the count returned and the string.
HARNESS = """#include <stdio.h>
#include <string.h>

int	ft_replace_${where}(char *str, char from, char to);

int	main(int ac, char **av)
{
	char	text[1024];
	int		count;

	(void)ac;
	strcpy(text, av[1]);
	count = ft_replace_${where}(text, av[2][0], av[3][0]);
	printf("%d %s\\n", count, text);
	return (0);
}
"""

EXERCISE = Exercise(
	name="replace_count",
	language="c",
	kind="function",
	assignment_name="ft_replace_${where}",
	expected_files=("ft_replace_${where}.c",),
	allowed_functions=(),
	themes=("char_replace",),
	params=(
		Param("where", ("word_start", "word_end", "in_runs", "inside"), {
			"word_start": "that start a word: the first character of the string, or one right\n"
				"after a space or a tab",
			"word_end": "that end a word: the last character of the string, or one right\n"
				"before a space or a tab",
			"in_runs": "that are in a run: next to another from (right before or right after\n"
				"it)",
			"inside": "that are neither the first nor the last character of the string",
		}),
	),
	subject=(
		"Write a function that replaces, in place, by the character to the\n"
		"occurrences of the character from in the string str\n"
		"$where.\n"
		"The other characters do not change. The function returns how many\n"
		"characters it replaced.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char *str, char from, char to);\n"
		"\n"
		"In the examples, the line below a call shows the int returned, then str\n"
		"after the call."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])}, {c_char(test.args[1])}, {c_char(test.args[2])})",
	examples=lambda params: {
		"word_start": (TestCase(("banana band", "b", "B")),),
		"word_end": (TestCase(("banana band", "a", "A")),),
		"in_runs": (TestCase(("aabaaa x a", "a", "-")),),
		"inside": (TestCase(("aaa", "a", "b")), TestCase(("aXa", "a", "b"))),
	}[params["where"]],
)
