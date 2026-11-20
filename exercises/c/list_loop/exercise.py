"""list_loop: an original function model in the style of "find a loop in a linked list".

The header ring.h is given next to the subject. The last node of the list
may point back to one of the nodes before it, making a loop. The function
returns the length of the loop, the index of its first node, or how many
nodes come before it. Whether there is a loop, a real 42 subject, is not
one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

HEADER = """#ifndef RING_H
# define RING_H

typedef struct s_ring
{
	int				value;
	struct s_ring	*next;
}	t_ring;

#endif
"""

def oracle(params, test):
	"""Return what the test main prints: the int returned, then a newline.

	args[0] is the index the last node points back to (-1: no loop), the
	other args are the values of the nodes.
	"""
	target, count = int(test.args[0]), len(test.args) - 1
	what = params["what"]
	looped = target >= 0 and count > 0
	if what == "length":
		result = count - target if looped else 0
	elif what == "start":
		result = target if looped else -1
	else:
		result = target if looped else count
	return f"{result}\n"

def generate_tests(params, rng):
	cases = [("-1",), ("-1", "5"), ("0", "5"), ("-1", "1", "2", "3"), ("1", "1", "2", "3"),
		("2", "1", "2", "3"), ("0", "4", "4", "4", "4"), ("3", "9", "8", "7", "6", "5")]
	for _ in range(8):
		count = rng.randint(1, 12)
		cases.append((str(rng.randint(-1, count - 1)),) + tuple(str(rng.randint(-9, 9)) for _ in range(count)))
	return [TestCase(case) for case in cases]

# The test main: av[1] is the index the last node points back to (-1: none),
# the next ones the values. It prints what the function returns.
HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include "ring.h"

int	ft_loop_${what}(t_ring *begin);

int	main(int ac, char **av)
{
	t_ring	*nodes[64];
	int		count;
	int		target;
	int		i;

	count = ac - 2;
	target = atoi(av[1]);
	i = 0;
	while (i < count)
	{
		nodes[i] = malloc(sizeof(t_ring));
		nodes[i]->value = atoi(av[i + 2]);
		nodes[i]->next = NULL;
		if (i > 0)
			nodes[i - 1]->next = nodes[i];
		i++;
	}
	if (count > 0 && target >= 0)
		nodes[count - 1]->next = nodes[target];
	printf("%d\\n", ft_loop_${what}(count > 0 ? nodes[0] : NULL));
	i = 0;
	while (i < count)
		free(nodes[i++]);
	return (0);
}
"""

def call(name, test):
	"""The call, with the list in a comment: where the last node points back."""
	values = test.args[1:]
	if not values:
		return f"{name}(NULL)"
	target = int(test.args[0])
	end = f"back to node {target}" if target >= 0 else "NULL"
	return f"{name}(list) /* {' -> '.join(values)} -> {end} */"

EXERCISE = Exercise(
	name="list_loop",
	language="c",
	kind="function",
	assignment_name="ft_loop_${what}",
	expected_files=("ft_loop_${what}.c",),
	allowed_functions=(),
	themes=("list_cycle",),
	params=(
		Param("what", ("length", "start", "before"), {
			"length": "how many nodes the loop has (0 if there is no loop)",
			"start": "the index, from 0, of the first node of the loop: the node the last one\n"
				"points back to (-1 if there is no loop)",
			"before": "how many nodes come before the loop (all of them if there is no loop)",
		}),
	),
	provided_files={"ring.h": HEADER},
	subject=(
		"In a linked list, the next of the last node may point back to one of the\n"
		"nodes (the last one included), making a loop; otherwise it is NULL. Write a\n"
		"function that takes the first node (NULL for an empty list) and returns\n"
		"$what.\n"
		"The list is not changed.\n"
		"\n"
		"The nodes are of the type t_ring, declared in the header ring.h, given next\n"
		"to this subject:\n"
		"\n"
		+ HEADER +
		"\n"
		"Include it in your file, but do not hand it in.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(t_ring *begin);\n"
		"\n"
		"In the examples, the comment shows the values of the list and where its\n"
		"last node points, and the line below shows the int returned."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(TestCase(("1", "1", "2", "3")), TestCase(("-1", "1", "2", "3")), TestCase(("-1",))),
)
