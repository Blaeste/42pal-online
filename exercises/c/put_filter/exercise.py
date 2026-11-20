"""put_filter: an original function model in the style of "display a string".

The student writes a void function that displays a string with write: its
letters only, its digits only, in uppercase, or each character twice, with
or without a newline after. Displaying the string as it is, a real 42
subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def oracle(params, test):
	"""Return what the function displays (the test main adds nothing)."""
	text = test.args[0]
	what = params["what"]
	if what == "letters":
		text = "".join(char for char in text if char.isascii() and char.isalpha())
	elif what == "digits":
		text = "".join(char for char in text if "0" <= char <= "9")
	elif what == "upper":
		text = "".join(char.upper() if "a" <= char <= "z" else char for char in text)
	else:
		text = "".join(char * 2 for char in text)
	return text + ("\n" if params["end"] == "newline" else "")

def generate_tests(params, rng):
	"""Return the test cases: fixed strings, then random ones."""
	texts = ["", "a1 B2!", "Hi 42", "ab ", "abc", "2024-11-18", "Hello, World!"]
	for _ in range(8):
		texts.append("".join(rng.choice("abYZ 07-!") for _ in range(rng.randint(1, 18))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; the function displays everything.
HARNESS = """void	ft_put_${what}_${end}(char *str);

int	main(int ac, char **av)
{
	(void)ac;
	ft_put_${what}_${end}(av[1]);
	return (0);
}
"""

EXERCISE = Exercise(
	name="put_filter",
	language="c",
	kind="function",
	assignment_name="ft_put_${what}_${end}",
	expected_files=("ft_put_${what}_${end}.c",),
	allowed_functions=("write",),
	themes=("string_print",),
	params=(
		Param("what", ("letters", "digits", "upper", "doubled"), {
			"letters": "keeping only its letters (a to z and A to Z), in their order",
			"digits": "keeping only its digits (0 to 9), in their order",
			"upper": "with its lowercase letters turned into uppercase",
			"doubled": "with each of its characters twice in a row",
		}),
		Param("end", ("bare", "newline"), {
			"bare": "Nothing is displayed after them",
			"newline": "A newline is displayed after them, even if nothing else was",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that displays, on the standard output, the string str\n"
		"$what.\n"
		"$end.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("Hello, World 42!",)), TestCase(("",))),
)
