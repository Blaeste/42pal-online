"""hop_range: an original function model in the style of "an array of numbers, from the end".

The student writes a function that returns a new array of ints, allocated
with malloc: the numbers from start towards end, or from end towards start,
every 2, 3 or 5. The test main frees it: leaks are checked. Every number
(a step of 1), a real 42 subject, is never the step.
"""

from pal42.model import Exercise, Param, TestCase

def numbers(start, end, step, direction):
	"""The numbers the array holds, in its order."""
	count = abs(end - start) // step + 1
	first, towards = (start, end) if direction == "forward" else (end, start)
	sign = 1 if towards >= first else -1
	return [first + sign * step * i for i in range(count)]

def oracle(params, test):
	"""Return what the test main prints: the numbers, separated by spaces, then a newline."""
	start, end = int(test.args[0]), int(test.args[1])
	return " ".join(map(str, numbers(start, end, int(params["step"]), params["direction"]))) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: the edge cases first (checked by valgrind), then random ones."""
	pairs = [(0, 0), (1, 10), (10, 1), (1, 9), (5, -3), (-7, 7), (-20, -1), (100, 3)]
	pairs += [(rng.randint(-50, 50), rng.randint(-50, 50)) for _ in range(8)]
	return [TestCase((str(a), str(b))) for a, b in pairs]

# The test main: av[1] is start, av[2] end; it prints the numbers, then frees them.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

int	*ft_hop_${step}_${direction}(int start, int end);

int	main(int ac, char **av)
{
	int	*numbers;
	int	start;
	int	end;
	int	count;
	int	i;

	(void)ac;
	start = atoi(av[1]);
	end = atoi(av[2]);
	count = abs(end - start) / ${step} + 1;
	numbers = ft_hop_${step}_${direction}(start, end);
	if (!numbers)
	{
		printf("(null)\\n");
		return (0);
	}
	i = 0;
	while (i < count)
	{
		if (i > 0)
			printf(" ");
		printf("%d", numbers[i++]);
	}
	printf("\\n");
	free(numbers);
	return (0);
}
"""

EXERCISE = Exercise(
	name="hop_range",
	language="c",
	kind="function",
	assignment_name="ft_hop_${step}_${direction}",
	expected_files=("ft_hop_${step}_${direction}.c",),
	allowed_functions=("malloc",),
	themes=("int_range_back",),
	params=(
		Param("step", ("2", "3", "5")),
		Param("direction", ("forward", "backward"), {
			"forward": "from start towards end (start first)",
			"backward": "from end towards start (end first)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns a new array of ints, allocated with malloc,\n"
		"holding numbers\n"
		"$step\n"
		"apart, going\n"
		"$direction,\n"
		"without going past the other end. The array holds\n"
		"(|end - start| / step) + 1 numbers; start and end may be in any order.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t*$assignment(int start, int end);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=lambda name, test: f"{name}({test.args[0]}, {test.args[1]})",
	examples=(TestCase(("1", "10")), TestCase(("1", "9")), TestCase(("5", "-3"))),
)
