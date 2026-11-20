"""sequence_array: an original function model on the theme "build an array of ints with malloc".

The student writes a function that returns a new array of n ints, allocated
with malloc, holding the first n terms of a sequence (squares, triangular
numbers, Fibonacci numbers, odd numbers or powers of two), in the order of
the sequence or in reverse order. The test main frees it: leaks are checked.
"""

from pal42.model import Exercise, Param, TestCase

# The k-th term of each sequence, k = 0, 1, 2... (Fibonacci is built apart).
FORMULAS = {
	"squares": lambda k: k * k,
	"triangles": lambda k: k * (k + 1) // 2,
	"odds": lambda k: 2 * k + 1,
	"powers_of_two": lambda k: 2 ** k,
}

def terms(sequence, n):
	"""The first n terms of `sequence`, in its order."""
	if sequence == "fibonacci":
		numbers = [0, 1]
		while len(numbers) < n:
			numbers.append(numbers[-1] + numbers[-2])
		return numbers[:n]
	return [FORMULAS[sequence](k) for k in range(n)]

def oracle(params, test):
	"""Return what the test main prints: the n ints, or (null), then a newline."""
	n = int(test.args[0])
	if n <= 0:
		return "(null)\n"
	numbers = terms(params["sequence"], n)
	if params["order"] == "down":
		numbers.reverse()
	return " ".join(map(str, numbers)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: the edge cases first (checked by valgrind), then random ones."""
	numbers = [0, -5, 1, 2, 31, 10, -2147483648]
	numbers += [rng.randint(1, 31) for _ in range(10)]
	return [TestCase((str(number),)) for number in numbers]

# The test main: av[1] is n; it prints the n ints of the array, then frees it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

int	*ft_${sequence}_${order}(int n);

int	main(int ac, char **av)
{
	int	*numbers;
	int	n;
	int	i;

	(void)ac;
	n = atoi(av[1]);
	numbers = ft_${sequence}_${order}(n);
	if (!numbers)
	{
		printf("(null)\\n");
		return (0);
	}
	i = 0;
	while (i < n)
	{
		if (i > 0)
			printf(" ");
		printf("%d", numbers[i]);
		i++;
	}
	printf("\\n");
	free(numbers);
	return (0);
}
"""

EXERCISE = Exercise(
	name="sequence_array",
	language="c",
	kind="function",
	assignment_name="ft_${sequence}_${order}",
	expected_files=("ft_${sequence}_${order}.c",),
	allowed_functions=("malloc", "free"),
	themes=("int_range",),
	params=(
		Param("sequence", ("squares", "triangles", "fibonacci", "odds", "powers_of_two"), {
			"squares": "square numbers: 0, 1, 4, 9, 16... (k * k for k = 0, 1, 2...)",
			"triangles": "triangular numbers: 0, 1, 3, 6, 10... (0 + 1 + ... + k for k = 0, 1, 2...)",
			"fibonacci": "Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8... (from the third one on,\n"
				"each is the sum of the two before it)",
			"odds": "odd numbers: 1, 3, 5, 7, 9...",
			"powers_of_two": "powers of two: 1, 2, 4, 8, 16... (2 to the power k for k = 0, 1, 2...)",
		}),
		Param("order", ("up", "down"), {
			"up": "in this order: the first one at index 0, the n-th one at index n - 1",
			"down": "in reverse order: the n-th one at index 0, the first one at index n - 1",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns a new array of n ints, allocated with malloc,\n"
		"holding the first n\n"
		"$sequence,\n"
		"$order.\n"
		"If n is 0 or less, it returns NULL. n is never more than 31.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t*$assignment(int n);\n"
		"\n"
		"In the examples, the line below each call shows the n ints of the array\n"
		"returned, separated by spaces."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=lambda name, test: f"{name}({test.args[0]})",
	examples=(
		TestCase(("6",)),
		TestCase(("1",)),
		TestCase(("0",)),
	),
)
