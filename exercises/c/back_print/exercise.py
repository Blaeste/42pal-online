"""back_print: an original function model in the style of "display a string
backwards".

The student writes a void function that displays with write a part of a
string from its end: its letters only, one character out of two, or each
of its lines turned around. The whole string backwards, the real 42
subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def backwards(text, what):
	if what == "letters_only":
		return "".join(char for char in reversed(text) if char.isascii() and char.isalpha())
	if what == "every_other":
		return text[::-1][::2]
	return "\n".join(line[::-1] for line in text.split("\n"))

def oracle(params, test):
	"""Return what the function displays: the part backwards, then a newline."""
	return backwards(test.args[0], params["what"]) + "\n"

def generate_tests(params, rng):
	texts = ["", "a1b-c", "abcdef", "ab\ncd", "x", "Hello, World!", "one\n\ntwo", "12345"]
	for _ in range(8):
		texts.append("".join(rng.choice("abC 1\n-") for _ in range(rng.randint(1, 14))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; the function displays it.
HARNESS = """void	ft_print_back_${what}(char *str);

int	main(int ac, char **av)
{
	(void)ac;
	ft_print_back_${what}(av[1]);
	return (0);
}
"""

EXERCISE = Exercise(
	name="back_print",
	language="c",
	kind="function",
	assignment_name="ft_print_back_${what}",
	expected_files=("ft_print_back_${what}.c",),
	allowed_functions=("write",),
	themes=("reverse_print",),
	params=(
		Param("what", ("letters_only", "every_other", "each_line"), {
			"letters_only": "its letters only (a to z and A to Z), from the last one to the first\n"
				"one",
			"every_other": "one character out of two from its end: the last character, the one\n"
				"two places before it, and so on",
			"each_line": "each of its lines turned around, the lines staying in their order (the\n"
				"lines are separated by newlines, which stay where they are)",
		}),
	),
	subject=(
		"Write a function that displays on the standard output\n"
		"$what,\n"
		"then a newline. str is the string given as its parameter.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=lambda params: {
		"letters_only": (TestCase(("a1b-c",)),),
		"every_other": (TestCase(("abcdef",)),),
		"each_line": (TestCase(("ab\ncd",)),),
	}[params["what"]],
)
