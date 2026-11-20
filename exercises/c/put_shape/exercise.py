"""put_shape: an original function model in the style of "display a string".

The student writes a void function that displays a string with write, in a
shape: its characters spaced out, between brackets, or each of its words on
a line of its own. Displaying the string as it is, the real 42 subject, is
not one of the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def shaped(text, how):
	if how == "spaced":
		return " ".join(text) + "\n"
	if how == "framed":
		return f"[{text}]\n"
	return "".join(word + "\n" for word in re.findall(r"[^ \t]+", text))

def oracle(params, test):
	"""Return what the function displays."""
	return shaped(test.args[0], params["how"])

def generate_tests(params, rng):
	texts = ["", "abc", "  hi \tthere ", "   ", "one", "a b", "42 is the answer!", "x"]
	for _ in range(8):
		texts.append("".join(rng.choice("ab cD\t9!") for _ in range(rng.randint(1, 14))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; the function displays it.
HARNESS = """void	ft_put_${how}(char *str);

int	main(int ac, char **av)
{
	(void)ac;
	ft_put_${how}(av[1]);
	return (0);
}
"""

EXERCISE = Exercise(
	name="put_shape",
	language="c",
	kind="function",
	assignment_name="ft_put_${how}",
	expected_files=("ft_put_${how}.c",),
	allowed_functions=("write",),
	themes=("string_print",),
	params=(
		Param("how", ("spaced", "framed", "words_lines"), {
			"spaced": "its characters with one space between each of them (none before the\n"
				"first one nor after the last one), then a newline",
			"framed": "a [, the string, a ], then a newline",
			"words_lines": "each of its words followed by a newline: a word a line, and nothing\n"
				"for a string with no word. A word is a group of characters that are not\n"
				"spaces nor tabs, as long as it can be",
		}),
	),
	subject=(
		"Write a function that displays on the standard output a string given as\n"
		"its parameter, in this shape:\n"
		"$how.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("abc",)), TestCase(("  hi \tthere ",)), TestCase(("",))),
)
