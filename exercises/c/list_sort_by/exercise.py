"""list_sort_by: an original function model in the style of "sort a linked list".

The header item.h, which declares the items, is given next to the subject.
The function sorts a linked list of ints by absolute value, even numbers
first, by last digit or by number of digits, in that order or in the exact
reverse, and returns its new first item. The test main frees the items:
leaks are checked. Sorting with a function given to compare, a real 42
subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

HEADER = """#ifndef ITEM_H
# define ITEM_H

typedef struct s_item
{
	int				key;
	struct s_item	*next;
}	t_item;

#endif
"""

# The place of a number in the order of each key; the value breaks the ties.
KEYS = {
	"absolute": lambda n: (abs(n), n),
	"parity": lambda n: (n % 2 != 0, n),
	"last_digit": lambda n: (abs(n) % 10, n),
	"digit_count": lambda n: (len(str(abs(n))), n),
}

def oracle(params, test):
	"""Return what the test main prints: the keys after the sort, or (empty)."""
	numbers = sorted((int(arg) for arg in test.args), key=KEYS[params["key"]],
		reverse=params["order"] == "down")
	return (" -> ".join(map(str, numbers)) or "(empty)") + "\n"

def generate_tests(params, rng):
	"""Return the test cases: the edge cases first (checked by valgrind), then random ones."""
	lists = [(), ("7",), ("3", "-1", "4", "-3", "0", "-5"), ("5", "2", "-3", "8"),
		("9", "8", "7", "6", "5", "4", "3", "2", "1", "0"), ("21", "13", "40", "-11")]
	for _ in range(8):
		lists.append(tuple(str(rng.randint(-150, 150)) for _ in range(rng.randint(2, 12))))
	return [TestCase(numbers) for numbers in lists]

# The test main: builds the list from av[1], av[2]..., sorts it, prints it, frees it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include "item.h"

t_item	*ft_list_sort_${key}_${order}(t_item *begin);

int	main(int ac, char **av)
{
	t_item	*list;
	t_item	**last;
	t_item	*next;
	int		i;

	list = NULL;
	last = &list;
	i = 1;
	while (i < ac)
	{
		*last = malloc(sizeof(t_item));
		(*last)->key = atoi(av[i]);
		(*last)->next = NULL;
		last = &(*last)->next;
		i++;
	}
	list = ft_list_sort_${key}_${order}(list);
	if (!list)
		printf("(empty)");
	while (list)
	{
		printf("%d", list->key);
		if (list->next)
			printf(" -> ");
		next = list->next;
		free(list);
		list = next;
	}
	printf("\\n");
	return (0);
}
"""

def call(name, test):
	"""The call shown in the examples and the traces, with the list in a comment."""
	return f"{name}(list) /* {' -> '.join(test.args) or '(empty)'} */"

EXERCISE = Exercise(
	name="list_sort_by",
	language="c",
	kind="function",
	assignment_name="ft_list_sort_${key}_${order}",
	expected_files=("ft_list_sort_${key}_${order}.c",),
	allowed_functions=(),
	themes=("list_sort",),
	params=(
		Param("key", ("absolute", "parity", "last_digit", "digit_count"), {
			"absolute": "by their absolute value, from the smallest; of two keys with the same\n"
				"absolute value, like -3 and 3, the negative one comes first",
			"parity": "the even keys first (0 included), then the odd ones; among the even\n"
				"keys, and among the odd ones, from the smallest",
			"last_digit": "by the last digit of their absolute value, from 0 to 9; among keys\n"
				"with the same last digit, from the smallest",
			"digit_count": "by the number of digits of their absolute value, from the fewest (0\n"
				"has one digit); among keys with as many digits, from the smallest",
		}),
		Param("order", ("up", "down"), {
			"up": "The sorted list follows this order: its first item comes first in it",
			"down": "The sorted list follows this order backwards: its first item is the one\n"
				"that comes last in it",
		}),
	),
	provided_files={"item.h": HEADER},
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that sorts a linked list by the keys of its items, and\n"
		"returns the first item of the sorted list (NULL for an empty list). No item\n"
		"may be lost.\n"
		"\n"
		"The order of the keys: $key.\n"
		"$order.\n"
		"\n"
		"The items are of the type t_item, declared in the header item.h, given next\n"
		"to this subject:\n"
		"\n"
		+ HEADER +
		"\n"
		"Include it in your file, but do not hand it in.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"t_item\t*$assignment(t_item *begin);\n"
		"\n"
		"In the examples, the comment shows the keys of the list before the call,\n"
		"from the first item, and the line below shows the list returned."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=call,
	examples=(TestCase(("3", "-1", "4", "-3", "0", "-5")), TestCase(())),
)
