"""bit_flip: an original function model in the style of "reverse the bits of a byte".

The student writes a function that reorders the bits of a byte: each half
turned around, each pair of bits swapped, or the six bits of the middle
turned around. The test main prints the byte returned in binary. All the
bits turned around, a real 42 subject, is not one of the parts.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the test main prints: the byte returned, in binary."""
	bits = format(int(test.args[0]) & 0xFF, "08b")
	part = params["part"]
	if part == "each_half":
		result = bits[3::-1] + bits[:3:-1]
	elif part == "pairs":
		result = "".join(bits[i + 1] + bits[i] for i in range(0, 8, 2))
	else:
		result = bits[0] + bits[6:0:-1] + bits[7]
	return result + "\n"

def generate_tests(params, rng):
	numbers = [0, 1, 128, 255, 38, 170, 85, 15, 240, 129]
	numbers += [rng.randint(0, 255) for _ in range(8)]
	return [TestCase((str(n),)) for n in numbers]

HARNESS = """#include <stdio.h>
#include <stdlib.h>

unsigned char	ft_reverse_${part}(unsigned char octet);

int	main(int ac, char **av)
{
	unsigned char	result;
	int				bit;

	(void)ac;
	result = ft_reverse_${part}((unsigned char)atoi(av[1]));
	bit = 8;
	while (bit--)
		putchar(((result >> bit) & 1) + '0');
	putchar('\\n');
	return (0);
}
"""

EXERCISE = Exercise(
	name="bit_flip",
	language="c",
	kind="function",
	assignment_name="ft_reverse_${part}",
	expected_files=("ft_reverse_${part}.c",),
	allowed_functions=(),
	themes=("bit_reverse",),
	params=(
		Param("part", ("each_half", "pairs", "middle_six"), {
			"each_half": "each of its two halves turned around on its own: the bits 7 6 5 4\n"
				"become 4 5 6 7, and the bits 3 2 1 0 become 0 1 2 3",
			"pairs": "each pair of bits swapped: bit 7 with bit 6, 5 with 4, 3 with 2, and\n"
				"1 with 0",
			"middle_six": "its six middle bits turned around (bits 6 to 1 become 1 to 6), the\n"
				"highest bit and the lowest one staying in their places",
		}),
	),
	subject=(
		"Write a function that takes a byte and returns it with\n"
		"$part.\n"
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
	call=lambda name, test: f"{name}({test.args[0]}) /* {int(test.args[0]):08b} */",
	examples=(TestCase(("38",)), TestCase(("15",))),
)
