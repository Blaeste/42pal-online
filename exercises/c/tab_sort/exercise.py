"""tab_sort: an original function model on the theme "sort an array of ints".

The student writes a function that sorts an array of ints in place, by
absolute value, even numbers first, by last digit or by number of digits,
in that order or in the exact reverse. Sorting by value alone, a real 42
subject, is not one of the keys.
"""

from pal42.model import Exercise, Param, TestCase

# For each key: the place of a number in the order, compared as a pair; the
# value itself breaks the ties, so that the order is total.
KEYS = {
	"absolute": lambda n: (abs(n), n),
	"parity": lambda n: (n % 2 != 0, n),
	"last_digit": lambda n: (abs(n) % 10, n),
	"digit_count": lambda n: (len(str(abs(n))), n),
}

def oracle(params, test):
	"""Return what the test main prints: the sorted array, then a newline."""
	numbers = sorted((int(arg) for arg in test.args), key=KEYS[params["key"]],
		reverse=params["order"] == "down")
	return " ".join(map(str, numbers)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: arrays with ties and signs first, then random ones."""
	arrays = [
		(),
		("5",),
		("3", "-1", "4", "-3", "0", "-5"),
		("5", "2", "-3", "8", "0", "7", "-4"),
		("21", "13", "40", "-11", "5", "33"),
		("100", "-7", "42", "0", "-55", "3"),
		("9", "8", "7", "6", "5", "4", "3", "2", "1", "0"),
	]
	for _ in range(10):
		arrays.append(tuple(str(rng.randint(-150, 150)) for _ in range(rng.randint(2, 15))))
	return [TestCase(numbers) for numbers in arrays]

# The test main: the array is av[1], av[2]... (NULL when there is none);
# it sorts it, then prints it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

void	ft_sort_by_${key}_${order}(int *tab, unsigned int size);

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
	ft_sort_by_${key}_${order}(tab, ac - 1);
	i = 0;
	while (i < ac - 1)
	{
		if (i > 0)
			printf(" ");
		printf("%d", numbers[i]);
		i++;
	}
	printf("\\n");
	return (0);
}
"""

def call(name, test):
	"""The call shown in the examples and the traces, as a C compound literal."""
	if not test.args:
		return f"{name}(NULL, 0)"
	return f"{name}((int[]){{{', '.join(test.args)}}}, {len(test.args)})"

EXERCISE = Exercise(
	name="tab_sort",
	language="c",
	kind="function",
	assignment_name="ft_sort_by_${key}_${order}",
	expected_files=("ft_sort_by_${key}_${order}.c",),
	allowed_functions=(),
	themes=("array_sort",),
	params=(
		Param("key", ("absolute", "parity", "last_digit", "digit_count"), {
			"absolute": "by absolute value; of two numbers as big, like -3 and 3, the\n"
				"negative one comes first",
			"parity": "the even numbers first (0 included), then the odd ones, each group\n"
				"in increasing order",
			"last_digit": "by the last digit of their absolute value, from 0 to 9; with the\n"
				"same last digit, in increasing order",
			"digit_count": "by the number of digits of their absolute value (0 has one); with\n"
				"as many digits, in increasing order",
		}),
		Param("order", ("up", "down"), {
			"up": "The array ends up in this order, from its first value to its last one",
			"down": "The array ends up in the exact reverse of this order: its first value\n"
				"is the one that this order puts last",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that sorts the array tab of size ints, in place, in this\n"
		"order:\n"
		"$key.\n"
		"$order.\n"
		"When size is 0, tab may be NULL.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(int *tab, unsigned int size);\n"
		"\n"
		"In the examples, each array is written as a C compound literal, and the\n"
		"line below shows the array once sorted."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(
		TestCase(("3", "-1", "4", "-3", "0", "-5")),
		TestCase(("21", "13", "40", "-11", "5", "33")),
		TestCase(()),
	),
)
