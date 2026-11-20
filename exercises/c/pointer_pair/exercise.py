"""pointer_pair: an original function model in the style of "exchange two ints".

The student writes a function that changes two ints through their addresses:
put them in increasing or decreasing order, put their sum and difference,
or exchange them while doubling or negating them. The plain exchange, a real
42 subject, is not one of the operations.
"""

from pal42.model import Exercise, Param, TestCase

def operate(operation, a, b):
	"""The new values of *a and *b."""
	if operation == "order_up":
		return min(a, b), max(a, b)
	if operation == "order_down":
		return max(a, b), min(a, b)
	if operation == "sum_diff":
		return a + b, a - b
	if operation == "swap_double":
		return 2 * b, 2 * a
	return -b, -a

def oracle(params, test):
	"""Return what the test main prints: *a and *b, then a newline."""
	a, b = operate(params["operation"], int(test.args[0]), int(test.args[1]))
	return f"{a} {b}\n"

def generate_tests(params, rng):
	"""Return the test cases: pairs in both orders, equal, signs, then random ones."""
	pairs = [(7, 3), (3, 7), (-2, 5), (0, 0), (5, 5), (-8, -9), (7, -3), (100000, -100000)]
	pairs += [(rng.randint(-5000, 5000), rng.randint(-5000, 5000)) for _ in range(8)]
	return [TestCase((str(a), str(b))) for a, b in pairs]

# The test main: av[1] and av[2] are the two ints; it prints them after the call.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

void	ft_${operation}(int *a, int *b);

int	main(int ac, char **av)
{
	int	a;
	int	b;

	(void)ac;
	a = atoi(av[1]);
	b = atoi(av[2]);
	ft_${operation}(&a, &b);
	printf("%d %d\\n", a, b);
	return (0);
}
"""

EXERCISE = Exercise(
	name="pointer_pair",
	language="c",
	kind="function",
	assignment_name="ft_${operation}",
	expected_files=("ft_${operation}.c",),
	allowed_functions=(),
	themes=("value_swap",),
	params=(
		Param("operation", ("order_up", "order_down", "sum_diff", "swap_double", "swap_negate"), {
			"order_up": "puts the two values in increasing order: the smaller one in *a, the\n"
				"bigger one in *b",
			"order_down": "puts the two values in decreasing order: the bigger one in *a, the\n"
				"smaller one in *b",
			"sum_diff": "puts in *a the sum of the two values, and in *b the first value minus\n"
				"the second one (the values from before the call)",
			"swap_double": "exchanges the two values, each one doubled: *a gets twice the old *b,\n"
				"*b gets twice the old *a",
			"swap_negate": "exchanges the two values, each one with its sign changed: *a gets\n"
				"minus the old *b, *b gets minus the old *a",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that takes the addresses of two ints and\n"
		"$operation.\n"
		"The results always fit in an int.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(int *a, int *b);\n"
		"\n"
		"In the examples, the comment shows the values before the call, and the line\n"
		"below shows *a and *b after the call."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}(&a, &b) /* a = {test.args[0]}, b = {test.args[1]} */",
	examples=(TestCase(("7", "3")), TestCase(("-2", "5"))),
)
