"""list_each: an original function model in the style of "apply a function to a list".

The header box.h is given next to the subject. The function applies a
function f to some nodes of a linked list: one out of two, all of them from
the last one, while the values are positive, or all but the first. The test
main shows in what order f was called, then the list after. All the nodes
in order, a real 42 subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

HEADER = """#ifndef BOX_H
# define BOX_H

typedef struct s_box
{
	int				value;
	struct s_box	*next;
}	t_box;

#endif
"""

def chosen(values, which):
	"""The indexes of the nodes f is applied to, in the order of the calls."""
	if which == "every_other":
		return list(range(0, len(values), 2))
	if which == "backwards":
		return list(range(len(values) - 1, -1, -1))
	if which == "from_second":
		return list(range(1, len(values)))
	indexes = []
	for i, value in enumerate(values):
		if value <= 0:
			break
		indexes.append(i)
	return indexes

def oracle(params, test):
	"""Return what the test main prints: the values f got, then the list after."""
	values = [int(arg) for arg in test.args]
	calls = chosen(values, params["which"])
	got = [values[i] for i in calls]
	for i in calls:
		values[i] *= 2
	return "f got:" + "".join(f" {v}" for v in got) + "\nlist:" + "".join(f" {v}" for v in values) + "\n"

def generate_tests(params, rng):
	lists = [(), ("5",), ("3", "-1", "4", "-1", "5"), ("1", "2", "3", "0", "4"), ("-2", "7"),
		("10", "20", "30", "40")]
	for _ in range(8):
		lists.append(tuple(str(rng.randint(-5, 50)) for _ in range(rng.randint(1, 10))))
	return [TestCase(values) for values in lists]

HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include "box.h"

void	ft_box_each_${which}(t_box *begin, void (*f)(int *));

/* f: shows the value it gets, then doubles it. */
static void	twice(int *value)
{
	printf(" %d", *value);
	*value *= 2;
}

int	main(int ac, char **av)
{
	t_box	*list;
	t_box	**last;
	t_box	*next;
	int		i;

	list = NULL;
	last = &list;
	i = 1;
	while (i < ac)
	{
		*last = malloc(sizeof(t_box));
		(*last)->value = atoi(av[i]);
		(*last)->next = NULL;
		last = &(*last)->next;
		i++;
	}
	printf("f got:");
	ft_box_each_${which}(list, &twice);
	printf("\\nlist:");
	while (list)
	{
		printf(" %d", list->value);
		next = list->next;
		free(list);
		list = next;
	}
	printf("\\n");
	return (0);
}
"""

def call(name, test):
	return f"{name}(list, &twice) /* {' -> '.join(test.args) or '(empty)'} */"

EXERCISE = Exercise(
	name="list_each",
	language="c",
	kind="function",
	assignment_name="ft_box_each_${which}",
	expected_files=("ft_box_each_${which}.c",),
	allowed_functions=(),
	themes=("list_apply",),
	params=(
		Param("which", ("every_other", "backwards", "while_positive", "from_second"), {
			"every_other": "one node out of two, from the first one: the first, the third, the\n"
				"fifth and so on",
			"backwards": "every node, from the last one to the first one",
			"while_positive": "the nodes from the first one, as long as their value is more than 0\n"
				"(it stops at the first node whose value is 0 or less, without calling f\n"
				"on it)",
			"from_second": "every node but the first one, in their order",
		}),
	),
	provided_files={"box.h": HEADER},
	subject=(
		"Write a function that takes the first node of a linked list of ints (NULL\n"
		"for an empty list) and a function f. It calls f once for each of these\n"
		"nodes:\n"
		"$which.\n"
		"Each call gives f the address of the value of the node.\n"
		"\n"
		"The nodes are of the type t_box, declared in the header box.h, given next\n"
		"to this subject:\n"
		"\n"
		+ HEADER +
		"\n"
		"Include it in your file, but do not hand it in.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(t_box *begin, void (*f)(int *));\n"
		"\n"
		"In the examples, f is a function that shows the value it gets, then\n"
		"doubles it: the first line below each call shows the values f got, in the\n"
		"order of the calls, and the second one the list after the call."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(TestCase(("3", "-1", "4", "-1", "5")), TestCase(())),
)
