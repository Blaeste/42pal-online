"""int_to_text: an original function model in the style of "an int into a string".

The student writes a function that returns a new string, allocated with
malloc, holding an int in base 10: in groups of three digits cut by spaces
or by commas, always with a sign, or with at least 6 digits. The test main
frees it: leaks are checked. The plain writing, a real 42 subject, is not
one of the formats.
"""

from pal42.model import Exercise, Param, TestCase

def grouped(digits, separator):
	"""The digits in groups of three counted from the right."""
	first = len(digits) % 3 or 3
	return separator.join([digits[:first]] + [digits[i:i + 3] for i in range(first, len(digits), 3)])

def oracle(params, test):
	"""Return what the test main prints: the string, then a newline."""
	n = int(test.args[0])
	sign = "-" if n < 0 else ""
	digits = str(abs(n))
	format = params["format"]
	if format == "spaced":
		return sign + grouped(digits, " ") + "\n"
	if format == "commas":
		return sign + grouped(digits, ",") + "\n"
	if format == "signed":
		return ("+" if n > 0 else sign) + digits + "\n"
	return sign + digits.rjust(6, "0") + "\n"

def generate_tests(params, rng):
	"""Return the test cases: the ends of int first (checked by valgrind), then random ones."""
	numbers = [0, -2147483648, 2147483647, -1, 42, 999, 1000, -123456, 1234567]
	numbers += [rng.randint(-2**31, 2**31 - 1) for _ in range(5)]
	numbers += [rng.randint(-5000, 5000) for _ in range(4)]
	return [TestCase((str(n),)) for n in numbers]

# The test main: av[1] is the number; it prints the string, then frees it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

char	*ft_int_to_${format}(int n);

int	main(int ac, char **av)
{
	char	*text;

	(void)ac;
	text = ft_int_to_${format}(atoi(av[1]));
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
	name="int_to_text",
	language="c",
	kind="function",
	assignment_name="ft_int_to_${format}",
	expected_files=("ft_int_to_${format}.c",),
	allowed_functions=("malloc",),
	themes=("number_to_string",),
	params=(
		Param("format", ("spaced", "commas", "signed", "padded"), {
			"spaced": "its digits in groups of three counted from the right, separated by\n"
				"one space, after a minus sign for a negative n (-1 234 567)",
			"commas": "its digits in groups of three counted from the right, separated by a\n"
				"comma, after a minus sign for a negative n (-1,234,567)",
			"signed": "always with a sign before its digits: + for a positive n, - for a\n"
				"negative one, and no sign for 0 (+42, -42, 0)",
			"padded": "with at least 6 digits, zeros added on the left, after a minus sign\n"
				"for a negative n (000042, -000042, 1234567)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns a new string, allocated with malloc, holding\n"
		"the int n written in base 10,\n"
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
	examples=(TestCase(("-1234567",)), TestCase(("42",)), TestCase(("0",))),
)
