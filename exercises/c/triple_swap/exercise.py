"""triple_swap: an original function model in the style of "exchange two ints".

The student writes a function that moves three ints around through their
addresses: turned to the left or to the right, or sorted in increasing or
decreasing order. The exchange of two ints, the real 42 subject, is not one
of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def moved(how, a, b, c):
	if how == "turn_left":
		return b, c, a
	if how == "turn_right":
		return c, a, b
	return tuple(sorted((a, b, c), reverse=how == "sort_down"))

def oracle(params, test):
	"""Return what the test main prints: *a, *b and *c after the call."""
	return " ".join(map(str, moved(params["how"], *map(int, test.args)))) + "\n"

def generate_tests(params, rng):
	triples = [(1, 2, 3), (3, -1, 2), (5, 5, 0), (0, 0, 0), (-7, 8, -9), (3, 2, 1), (2, 3, 1), (100000, -5, 42)]
	triples += [tuple(rng.randint(-500, 500) for _ in range(3)) for _ in range(8)]
	return [TestCase(tuple(map(str, triple))) for triple in triples]

# The test main: av[1] to av[3] are the three ints; it prints them after the call.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

void	ft_three_${how}(int *a, int *b, int *c);

int	main(int ac, char **av)
{
	int	a;
	int	b;
	int	c;

	(void)ac;
	a = atoi(av[1]);
	b = atoi(av[2]);
	c = atoi(av[3]);
	ft_three_${how}(&a, &b, &c);
	printf("%d %d %d\\n", a, b, c);
	return (0);
}
"""

EXERCISE = Exercise(
	name="triple_swap",
	language="c",
	kind="function",
	assignment_name="ft_three_${how}",
	expected_files=("ft_three_${how}.c",),
	allowed_functions=(),
	themes=("value_swap",),
	params=(
		Param("how", ("turn_left", "turn_right", "sort_up", "sort_down"), {
			"turn_left": "turns the three values to the left: *a gets the old *b, *b the old *c,\n"
				"and *c the old *a",
			"turn_right": "turns the three values to the right: *a gets the old *c, *b the old *a,\n"
				"and *c the old *b",
			"sort_up": "puts the three values in increasing order: the smallest in *a, the\n"
				"largest in *c",
			"sort_down": "puts the three values in decreasing order: the largest in *a, the\n"
				"smallest in *c",
		}),
	),
	subject=(
		"Write a function that takes the addresses of three ints and\n"
		"$how.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(int *a, int *b, int *c);\n"
		"\n"
		"In the examples, the comment shows the values before the call, and the line\n"
		"below shows *a, *b and *c after the call."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}(&a, &b, &c) /* a = {test.args[0]}, b = {test.args[1]}, c = {test.args[2]} */",
	examples=(TestCase(("1", "2", "3")), TestCase(("3", "-1", "2"))),
)
