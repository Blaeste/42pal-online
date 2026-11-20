"""dup_shape: an original function model in the style of "duplicate a string".

The student writes a function that returns a new string, allocated with
malloc: the string given reversed, with each character twice, twice in a
row, without the spaces and tabs at both ends, or in uppercase. The test
main frees it: leaks are checked. The plain copy, a real 42 subject, is not
one of the shapes.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def shaped(text, shape):
	"""The new string the function returns."""
	if shape == "reversed":
		return text[::-1]
	if shape == "doubled":
		return "".join(char * 2 for char in text)
	if shape == "twice":
		return text * 2
	if shape == "trimmed":
		return text.strip(" \t")
	return "".join(char.upper() if "a" <= char <= "z" else char for char in text)

def oracle(params, test):
	"""Return what the test main prints: the string, then a newline."""
	return shaped(test.args[0], params["shape"]) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: the edge cases first (checked by valgrind), then random ones."""
	texts = ["", "x", " \t a b \t", "   ", "Hello, World 42!", "abc"]
	for _ in range(8):
		texts.append("".join(rng.choice("abXY 12\t-") for _ in range(rng.randint(1, 20))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; it prints the new string, then frees it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

char	*ft_dup_${shape}(char *src);

int	main(int ac, char **av)
{
	char	*copy;

	(void)ac;
	copy = ft_dup_${shape}(av[1]);
	if (!copy)
	{
		printf("(null)\\n");
		return (0);
	}
	printf("%s\\n", copy);
	free(copy);
	return (0);
}
"""

EXERCISE = Exercise(
	name="dup_shape",
	language="c",
	kind="function",
	assignment_name="ft_dup_${shape}",
	expected_files=("ft_dup_${shape}.c",),
	allowed_functions=("malloc",),
	themes=("string_dup",),
	params=(
		Param("shape", ("reversed", "doubled", "twice", "trimmed", "upper"), {
			"reversed": "src with its characters in reverse order",
			"doubled": "src with each of its characters twice in a row",
			"twice": "src twice in a row",
			"trimmed": "src without the spaces and tabs at its start and at its end",
			"upper": "src with its lowercase letters turned into uppercase",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns a new string, allocated with malloc, holding\n"
		"$shape.\n"
		"src is never changed.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *src);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("  Hello, World 42! ",)), TestCase(("",))),
)
