"""byte_show: an original function model in the style of "display the bits of a byte".

The student writes a void function that displays a byte: its bits from the
lowest one, its bits in two groups of four, its bits as dots and hashes, or
the byte in hexadecimal or in octal, with no newline. Its 8 bits from the
highest one, a real 42 subject, is not one of the forms.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the function displays (the test main adds nothing)."""
	byte = int(test.args[0]) & 0xFF
	bits = format(byte, "08b")
	form = params["form"]
	if form == "lsb_first":
		return bits[::-1]
	if form == "grouped":
		return f"{bits[:4]} {bits[4:]}"
	if form == "dots":
		return bits.replace("0", ".").replace("1", "#")
	if form == "hex":
		return format(byte, "02x")
	return format(byte, "03o")

def generate_tests(params, rng):
	"""Return the test cases: bytes with a clear pattern, then random ones."""
	numbers = [0, 1, 2, 38, 128, 170, 85, 255, 16, 15]
	numbers += [rng.randint(0, 255) for _ in range(8)]
	return [TestCase((str(n),)) for n in numbers]

# The test main: av[1] is the byte; the function displays everything.
HARNESS = """#include <stdlib.h>

void	ft_show_${form}(unsigned char octet);

int	main(int ac, char **av)
{
	(void)ac;
	ft_show_${form}((unsigned char)atoi(av[1]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="byte_show",
	language="c",
	kind="function",
	assignment_name="ft_show_${form}",
	expected_files=("ft_show_${form}.c",),
	allowed_functions=("write",),
	themes=("bit_print",),
	params=(
		Param("form", ("lsb_first", "grouped", "dots", "hex", "octal"), {
			"lsb_first": "its 8 bits, as 0 and 1, from the lowest one to the highest one",
			"grouped": "its 8 bits, as 0 and 1, from the highest one, in two groups of four\n"
				"separated by one space",
			"dots": "its 8 bits from the highest one, a . for each 0 and a # for each 1",
			"hex": "its value in hexadecimal, always with 2 digits (lowercase a to f)",
			"octal": "its value in octal, always with 3 digits",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that takes a byte and displays\n"
		"$form,\n"
		"with nothing after (no newline).\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(unsigned char octet);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({test.args[0]}) /* {int(test.args[0]):08b} */",
	examples=(TestCase(("38",)), TestCase(("255",)), TestCase(("1",))),
)
