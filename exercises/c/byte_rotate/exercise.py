"""byte_rotate: an original function model on the theme "bits".

The student writes a function that rotates the 8 bits of a byte to the left
or to the right by 1, 2 or 3 positions (the bits that go out on one side come
back in on the other side), then may invert every bit of the result.
The rotation by 4, which swaps the two halves of the byte, is left out: it is
a real 42 subject.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the test main prints: the byte returned, in binary."""
	byte = int(test.args[0]) & 0xFF
	amount = int(params["amount"])
	if params["way"] == "left":
		result = (byte << amount) | (byte >> (8 - amount))
	else:
		result = (byte >> amount) | (byte << (8 - amount))
	result &= 0xFF
	if params["invert"] == "flip":
		result ^= 0xFF
	return format(result, "08b") + "\n"

def generate_tests(params, rng):
	"""Return the test cases: the bytes with a clear pattern first, then random ones."""
	numbers = [0, 1, 128, 255, 38, 170, 85, 129]
	numbers += [rng.randint(0, 255) for _ in range(10)]
	return [TestCase((str(number),)) for number in numbers]

# The test main: av[1] is the byte; it prints the byte returned, in binary.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

unsigned char	ft_rotate_${way}_${amount}_${invert}(unsigned char octet);

int	main(int ac, char **av)
{
	unsigned char	result;
	int				bit;

	(void)ac;
	result = ft_rotate_${way}_${amount}_${invert}((unsigned char)atoi(av[1]));
	bit = 8;
	while (bit--)
		putchar(((result >> bit) & 1) + '0');
	putchar('\\n');
	return (0);
}
"""

def call(name, test):
	"""The call shown in the examples and the traces, with the byte in binary."""
	byte = int(test.args[0])
	return f"{name}({byte}) /* {byte:08b} */"

EXERCISE = Exercise(
	name="byte_rotate",
	language="c",
	kind="function",
	assignment_name="ft_rotate_${way}_${amount}_${invert}",
	expected_files=("ft_rotate_${way}_${amount}_${invert}.c",),
	allowed_functions=(),
	themes=("bit_rotate",),
	params=(
		Param("way", ("left", "right"), {
			"left": "to the left (toward the most significant bit)",
			"right": "to the right (toward the least significant bit)",
		}),
		Param("amount", ("1", "2", "3"), {
			"1": "1 position",
			"2": "2 positions",
			"3": "3 positions",
		}),
		Param("invert", ("keep", "flip"), {
			"keep": "It returns the rotated byte as it is",
			"flip": "Then it inverts every bit of the rotated byte (each 0 becomes 1\n"
				"and each 1 becomes 0) and returns the result",
		}),
	),
	subject=(
		"Write a function that takes a byte, octet, and returns it with its 8 bits\n"
		"rotated by $amount $way.\n"
		"Each bit that goes out on one side comes back in on the other side.\n"
		"$invert.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"unsigned char\t$assignment(unsigned char octet);\n"
		"\n"
		"In the examples, the comment shows the byte given in binary, and the line\n"
		"below shows the byte returned, in binary too."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(
		TestCase(("38",)),
		TestCase(("129",)),
		TestCase(("255",)),
	),
)
