"""tab_index: an original function model on the theme "go through an array of ints".

The student writes a function that returns the index of the first or the
last value of an array that is the biggest, the smallest, negative, even,
or already seen earlier in the array; -1 when there is none. With no value
at all, the array may be NULL: the test main does pass NULL then.
"""

from pal42.model import Exercise, Param, TestCase

def matching(rule, numbers):
	"""The indexes of the values that follow `rule`, in order."""
	if not numbers:
		return []
	if rule == "biggest":
		return [i for i, n in enumerate(numbers) if n == max(numbers)]
	if rule == "smallest":
		return [i for i, n in enumerate(numbers) if n == min(numbers)]
	if rule == "negative":
		return [i for i, n in enumerate(numbers) if n < 0]
	if rule == "even":
		return [i for i, n in enumerate(numbers) if n % 2 == 0]
	return [i for i, n in enumerate(numbers) if n in numbers[:i]]

def oracle(params, test):
	"""Return what the test main prints: the index returned, then a newline."""
	found = matching(params["rule"], [int(arg) for arg in test.args])
	if not found:
		return "-1\n"
	return f"{found[0] if params['which'] == 'first' else found[-1]}\n"

def generate_tests(params, rng):
	"""Return the test cases: arrays with a clear answer first, then random ones."""
	arrays = [
		(),
		("42",),
		("3", "-1", "4", "-1", "5", "9", "2", "6", "5", "3", "5"),
		("7", "7", "7"),
		("1", "3", "5"),
		("-8", "-2", "-8", "0"),
	]
	for _ in range(10):
		arrays.append(tuple(str(rng.randint(-20, 20)) for _ in range(rng.randint(1, 12))))
	return [TestCase(numbers) for numbers in arrays]

# The test main: the array is av[1], av[2]... (NULL when there is none);
# it prints the index returned.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

int	ft_index_${which}_${rule}(int *tab, unsigned int len);

int	main(int ac, char **av)
{
	int	numbers[64];
	int	*tab;
	int	i;

	tab = NULL;
	if (ac > 1)
		tab = numbers;
	i = 1;
	while (i < ac)
	{
		numbers[i - 1] = atoi(av[i]);
		i++;
	}
	printf("%d\\n", ft_index_${which}_${rule}(tab, ac - 1));
	return (0);
}
"""

def call(name, test):
	"""The call shown in the examples and the traces, as a C compound literal."""
	if not test.args:
		return f"{name}(NULL, 0)"
	return f"{name}((int[]){{{', '.join(test.args)}}}, {len(test.args)})"

EXERCISE = Exercise(
	name="tab_index",
	language="c",
	kind="function",
	assignment_name="ft_index_${which}_${rule}",
	expected_files=("ft_index_${which}_${rule}.c",),
	allowed_functions=(),
	themes=("array_search",),
	params=(
		Param("which", ("first", "last"), {
			"first": "the first value (the one with the smallest index)",
			"last": "the last value (the one with the biggest index)",
		}),
		Param("rule", ("biggest", "smallest", "negative", "even", "repeated"), {
			"biggest": "that is the biggest of the array",
			"smallest": "that is the smallest of the array",
			"negative": "that is negative",
			"even": "that is even (0 included)",
			"repeated": "that is already in the array at a smaller index",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that takes an array of len ints and returns the index of\n"
		"$which\n"
		"$rule.\n"
		"If no value is such, or if len is 0, it returns -1. When len is 0, tab may\n"
		"be NULL.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(int *tab, unsigned int len);\n"
		"\n"
		"In the examples, each array is written as a C compound literal, and the\n"
		"line below shows the index returned."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(
		TestCase(("3", "-1", "4", "-1", "5", "9", "2", "6", "5", "3", "5")),
		TestCase(("7", "7", "7")),
		TestCase(()),
	),
)
