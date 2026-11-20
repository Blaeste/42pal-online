"""list_measure: an original function model on the theme "go through a linked list".

The header cell.h, which declares the cells, is given next to the subject:
the student includes it and does not hand it in. The function goes through
a linked list of ints, all its cells or one out of two, and returns their
sum, the biggest or the smallest number, or how many are even or negative.
Counting the cells, which is a real 42 subject, is not one of the measures.
"""

from pal42.model import Exercise, Param, TestCase

# The header given with the subject, shown as it is in the subject too.
HEADER = """#ifndef CELL_H
# define CELL_H

typedef struct s_cell
{
	int				number;
	struct s_cell	*next;
}	t_cell;

#endif
"""

def measure(name, numbers):
	"""The measure `name` of `numbers`; 0 when there is none."""
	if not numbers:
		return 0
	if name == "sum":
		return sum(numbers)
	if name == "max":
		return max(numbers)
	if name == "min":
		return min(numbers)
	if name == "count_even":
		return sum(1 for number in numbers if number % 2 == 0)
	return sum(1 for number in numbers if number < 0)

def oracle(params, test):
	"""Return what the test main prints: the int returned, then a newline."""
	numbers = [int(arg) for arg in test.args]
	if params["cells"] == "every_other":
		numbers = numbers[::2]
	return f"{measure(params['measure'], numbers)}\n"

def generate_tests(params, rng):
	"""Return the test cases: lists with a clear answer first, then random ones."""
	lists = [
		(),
		("7",),
		("3", "-1", "4", "-1", "5"),
		("-8", "2", "-6", "0"),
		("0", "0"),
		("-5", "-9", "-1", "-7"),
	]
	for _ in range(10):
		lists.append(tuple(str(rng.randint(-50, 50)) for _ in range(rng.randint(1, 12))))
	return [TestCase(numbers) for numbers in lists]

# The test main: builds the list from av[1], av[2]..., prints what the
# function returns, then frees the list.
HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include "cell.h"

int	ft_list_${measure}_${cells}(t_cell *begin);

int	main(int ac, char **av)
{
	t_cell	*list;
	t_cell	**last;
	t_cell	*next;
	int		i;

	list = NULL;
	last = &list;
	i = 1;
	while (i < ac)
	{
		*last = malloc(sizeof(t_cell));
		(*last)->number = atoi(av[i]);
		(*last)->next = NULL;
		last = &(*last)->next;
		i++;
	}
	printf("%d\\n", ft_list_${measure}_${cells}(list));
	while (list)
	{
		next = list->next;
		free(list);
		list = next;
	}
	return (0);
}
"""

def call(name, test):
	"""The call shown in the examples and the traces, with the list in a comment."""
	numbers = " -> ".join(test.args) or "(empty)"
	return f"{name}(list) /* {numbers} */"

EXERCISE = Exercise(
	name="list_measure",
	language="c",
	kind="function",
	assignment_name="ft_list_${measure}_${cells}",
	expected_files=("ft_list_${measure}_${cells}.c",),
	allowed_functions=(),
	themes=("list_walk",),
	params=(
		Param("measure", ("sum", "max", "min", "count_even", "count_negative"), {
			"sum": "the sum of the numbers",
			"max": "the biggest number",
			"min": "the smallest number",
			"count_even": "how many numbers are even (0 included)",
			"count_negative": "how many numbers are negative",
		}),
		Param("cells", ("all", "every_other"), {
			"all": "all its cells",
			"every_other": "one cell out of two (the first, the third, the fifth and so on)",
		}),
	),
	provided_files={"cell.h": HEADER},
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that takes the first cell of a linked list of ints and,\n"
		"looking at\n"
		"$cells,\n"
		"returns\n"
		"$measure.\n"
		"For an empty list (NULL), it returns 0.\n"
		"\n"
		"The cells are of the type t_cell, declared in the header cell.h, given next\n"
		"to this subject:\n"
		"\n"
		+ HEADER +
		"\n"
		"Include it in your file, but do not hand it in.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(t_cell *begin);\n"
		"\n"
		"In the examples, the comment shows the numbers of the list, from the first\n"
		"cell, and the line below shows the int returned."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(
		TestCase(("3", "-1", "4", "-1", "5")),
		TestCase(("-8", "2", "-6", "0")),
		TestCase(()),
	),
)
