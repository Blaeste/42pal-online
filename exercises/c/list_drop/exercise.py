"""list_drop: an original function model on the theme "change a linked list".

The student hands in a function and the header node.h that declares the
nodes. The function removes from a linked list of ints every node, the first
one or the last one whose value is even, odd, negative or already seen
earlier in the list, and frees it. The test main frees the nodes left:
leaks are checked, so a node removed but not freed is found.
"""

from pal42.model import Exercise, Param, TestCase

# The header the student hands in, shown as it is in the subject; the same
# file is next to ref.c, for check-catalog.
HEADER = """#ifndef NODE_H
# define NODE_H

typedef struct s_node
{
	int				value;
	struct s_node	*next;
}	t_node;

#endif
"""

def matches(condition, values, index):
	"""True if the node at `index` meets `condition`."""
	value = values[index]
	if condition == "even":
		return value % 2 == 0
	if condition == "odd":
		return value % 2 != 0
	if condition == "negative":
		return value < 0
	return value in values[:index]

def oracle(params, test):
	"""Return what the test main prints: the values left, or (empty), then a newline."""
	values = [int(arg) for arg in test.args]
	found = [i for i in range(len(values)) if matches(params["condition"], values, i)]
	if params["which"] == "first":
		found = found[:1]
	elif params["which"] == "last":
		found = found[-1:]
	left = [value for i, value in enumerate(values) if i not in found]
	if not left:
		return "(empty)\n"
	return " -> ".join(map(str, left)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: lists made to drop at both ends first, then random ones."""
	lists = [
		(),
		("4",),
		("2", "2", "3", "-4", "-4", "5", "2"),
		("-1", "-1", "-1"),
		("7", "8", "7", "-6", "8", "9"),
		("0", "1", "-2", "3", "3"),
		("5", "-3", "5", "-3"),
	]
	for _ in range(10):
		length = rng.randint(1, 12)
		lists.append(tuple(str(rng.randint(-9, 9)) for _ in range(length)))
	return [TestCase(values) for values in lists]

# The test main: builds the list from av[1], av[2]..., calls the function,
# prints the values left, then frees the nodes left.
HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include "node.h"

void	ft_drop_${which}_${condition}(t_node **begin);

static void	print_list(t_node *node)
{
	if (!node)
		printf("(empty)");
	while (node)
	{
		printf("%d", node->value);
		if (node->next)
			printf(" -> ");
		node = node->next;
	}
	printf("\\n");
}

int	main(int ac, char **av)
{
	t_node	*list;
	t_node	**last;
	t_node	*next;
	int		i;

	list = NULL;
	last = &list;
	i = 1;
	while (i < ac)
	{
		*last = malloc(sizeof(t_node));
		(*last)->value = atoi(av[i]);
		(*last)->next = NULL;
		last = &(*last)->next;
		i++;
	}
	ft_drop_${which}_${condition}(&list);
	print_list(list);
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
	"""The call shown in the examples and the traces, with the list before it."""
	values = " -> ".join(test.args) or "(empty)"
	return f"{name}(&list) /* {values} */"

EXERCISE = Exercise(
	name="list_drop",
	language="c",
	kind="function",
	assignment_name="ft_drop_${which}_${condition}",
	expected_files=("ft_drop_${which}_${condition}.c", "node.h"),
	allowed_functions=("free",),
	themes=("list_remove",),
	params=(
		Param("which", ("all", "first", "last"), {
			"all": "every node",
			"first": "only the first node",
			"last": "only the last node",
		}),
		Param("condition", ("even", "odd", "negative", "repeated"), {
			"even": "whose value is even (0 included)",
			"odd": "whose value is odd",
			"negative": "whose value is negative",
			"repeated": "whose value is already in a node before it",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that takes the address of the first node of a linked list\n"
		"of ints and removes from the list\n"
		"$which\n"
		"$condition.\n"
		"Each node removed is freed with free; the other nodes stay in their order.\n"
		"If no node is to be removed, the list does not change. If the first node is\n"
		"removed, *begin becomes the new first node, or NULL if no node is left.\n"
		"\n"
		"The nodes are of the type t_node. Hand in, with your function, the header\n"
		"node.h with exactly this content:\n"
		"\n"
		+ HEADER +
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(t_node **begin);\n"
		"\n"
		"In the examples, the comment shows the values of the list before the call,\n"
		"from the first node, and the line below shows the list after the call."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=call,
	examples=(
		TestCase(("2", "2", "3", "-4", "-4", "5", "2")),
		TestCase(("7", "8", "7", "-6", "8", "9")),
		TestCase(("1",)),
	),
)
