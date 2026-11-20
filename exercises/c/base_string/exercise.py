"""base_string: an original function model on the theme "turn an integer into a string".

The student writes a function that returns a new string, allocated with
malloc, holding an int written in binary, octal or hexadecimal, with or
without a prefix (0b, 0o, 0x). The test main frees it: leaks are checked.
"""

from pal42.model import Exercise, Param, TestCase

# The format letter of Python's format() and the prefix of each base.
BASES = {"binary": ("b", "0b"), "octal": ("o", "0o"), "hex": ("x", "0x")}

def oracle(params, test):
	"""Return what the test main prints: the string, then a newline."""
	number = int(test.args[0])
	letter, prefix = BASES[params["base"]]
	digits = format(abs(number), letter)
	sign = "-" if number < 0 else ""
	if params["format"] == "plain":
		prefix = ""
	return f"{sign}{prefix}{digits}\n"

def generate_tests(params, rng):
	"""Return the test cases: the ends of int first (checked by valgrind), then random ones."""
	numbers = [0, 1, -1, 2147483647, -2147483648, 255, -256, 4096]
	numbers += [rng.randint(-2**31, 2**31 - 1) for _ in range(10)]
	return [TestCase((str(number),)) for number in numbers]

# The test main: av[1] is the number; it prints the string, then frees it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

char	*ft_${base}_string_${format}(int n);

int	main(int ac, char **av)
{
	char	*text;

	(void)ac;
	text = ft_${base}_string_${format}(atoi(av[1]));
	if (!text)
	{
		printf("(null)\\n");
		return (0);
	}
	printf("%s\\n", text);
	free(text);
	return (0);
}
"""

EXERCISE = Exercise(
	name="base_string",
	language="c",
	kind="function",
	assignment_name="ft_${base}_string_${format}",
	expected_files=("ft_${base}_string_${format}.c",),
	allowed_functions=("malloc",),
	themes=("base_to_string",),
	params=(
		Param("base", ("binary", "octal", "hex"), {
			"binary": "in binary (base 2)",
			"octal": "in octal (base 8)",
			"hex": "in hexadecimal (base 16, with the lowercase letters a to f)",
		}),
		Param("format", ("plain", "prefixed"), {
			"plain": "Nothing comes before the digits, but a minus sign for a negative n",
			"prefixed": "The digits come after a prefix, 0b, 0o or 0x for bases 2, 8 and 16;\n"
				"a minus sign, for a negative n, comes before the prefix",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns a new string, allocated with malloc, holding\n"
		"the int n written\n"
		"$base.\n"
		"$format.\n"
		"It works for every int, from -2147483648 to 2147483647.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(int n);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=lambda name, test: f"{name}({test.args[0]})",
	examples=(
		TestCase(("42",)),
		TestCase(("-255",)),
		TestCase(("0",)),
	),
)
