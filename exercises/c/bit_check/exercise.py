"""bit_check: an original function model in the style of "is it a power of 2".

The student writes a function that tells, from its bits, whether an
unsigned int is a power of 4, made of ones only, made of alternating bits,
a palindrome in binary, or made of exactly two ones. A power of 2, a real
42 subject, is not one of the properties.
"""

from pal42.model import Exercise, Param, TestCase

def holds(property, n):
	"""True if n has `property` (never for 0)."""
	bits = format(n, "b")
	if n == 0:
		return False
	if property == "power_of_4":
		return n & (n - 1) == 0 and (len(bits) - 1) % 2 == 0
	if property == "all_ones":
		return n & (n + 1) == 0
	if property == "alternating":
		return all(a != b for a, b in zip(bits, bits[1:]))
	if property == "bit_palindrome":
		return bits == bits[::-1]
	return bits.count("1") == 2

def oracle(params, test):
	"""Return what the test main prints: 1 or 0, then a newline."""
	return f"{int(holds(params['property'], int(test.args[0])))}\n"

def generate_tests(params, rng):
	"""Return the test cases: small numbers, the biggest ones, then random ones."""
	numbers = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 16, 21, 64, 255, 256, 1024, 2147483648,
		1073741824, 2863311530, 1431655765, 4294967295, 4294967294]
	numbers += [rng.randint(0, 2**32 - 1) for _ in range(6)]
	numbers += [rng.randint(0, 300) for _ in range(6)]
	return [TestCase((str(n),)) for n in numbers]

# The test main: av[1] is the number; it prints what the function returns.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

int	ft_is_${property}(unsigned int n);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\\n", ft_is_${property}((unsigned int)strtoul(av[1], NULL, 10)));
	return (0);
}
"""

EXERCISE = Exercise(
	name="bit_check",
	language="c",
	kind="function",
	assignment_name="ft_is_${property}",
	expected_files=("ft_is_${property}.c",),
	allowed_functions=(),
	themes=("bit_test",),
	params=(
		Param("property", ("power_of_4", "all_ones", "alternating", "bit_palindrome", "two_ones"), {
			"power_of_4": "a power of 4: 1, 4, 16, 64 and so on",
			"all_ones": "written in binary with ones only: 1, 3 (11), 7 (111) and so on",
			"alternating": "written in binary with bits that alternate, no two next to each other\n"
				"being the same: 1, 2 (10), 5 (101), 10 (1010) and so on",
			"bit_palindrome": "written in binary (without the zeros on the left) the same way from\n"
				"both ends: 1, 3 (11), 5 (101), 9 (1001) and so on",
			"two_ones": "written in binary with exactly two ones: 3 (11), 5 (101), 6 (110)\n"
				"and so on",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns 1 if the unsigned int n is\n"
		"$property;\n"
		"otherwise, and for 0, it returns 0.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(unsigned int n);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({test.args[0]}) /* {int(test.args[0]):b} */",
	examples=(TestCase(("5",)), TestCase(("16",)), TestCase(("0",))),
)
