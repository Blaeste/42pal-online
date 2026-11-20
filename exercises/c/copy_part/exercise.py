"""copy_part: an original function model in the style of "copy a string".

The student writes a function that copies a part of a string into a given
buffer: its first n characters, its last n characters, or all but its first
n characters, always with the ending '\\0', and returns the buffer. The copy
of the whole string, the real 42 subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def part(text, how, n):
	if how == "first_n":
		return text[:n]
	if how == "last_n":
		return text[len(text) - min(n, len(text)):]
	return text[n:]

def oracle(params, test):
	"""Return what the test main prints: the buffer after the call, then a newline."""
	return part(test.args[0], params["how"], int(test.args[1])) + "\n"

def generate_tests(params, rng):
	pairs = [("hello", 2), ("hello", 9), ("hello", 0), ("", 3), ("hello", 5), ("a b c", 1), ("tail", 3)]
	for _ in range(8):
		text = "".join(rng.choice("abcdXY 1") for _ in range(rng.randint(0, 12)))
		pairs.append((text, rng.randint(0, 14)))
	return [TestCase((text, str(n))) for text, n in pairs]

# The test main: av[1] is src, av[2] is n. The buffer is filled with X before
# the call, so that a missing '\\0' shows; it says so if another pointer than
# the buffer is returned.
HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char	*ft_copy_${how}(char *dst, char *src, int n);

int	main(int ac, char **av)
{
	char	buffer[256];

	(void)ac;
	memset(buffer, 'X', 255);
	buffer[255] = '\\0';
	if (ft_copy_${how}(buffer, av[1], atoi(av[2])) != buffer)
		printf("(the pointer returned is not dst) ");
	printf("%s\\n", buffer);
	return (0);
}
"""

EXERCISE = Exercise(
	name="copy_part",
	language="c",
	kind="function",
	assignment_name="ft_copy_${how}",
	expected_files=("ft_copy_${how}.c",),
	allowed_functions=(),
	themes=("string_copy",),
	params=(
		Param("how", ("first_n", "last_n", "from_n"), {
			"first_n": "the first n characters of src (all of them if src has fewer)",
			"last_n": "the last n characters of src (all of them if src has fewer)",
			"from_n": "the characters of src after its first n ones (nothing if src has n\n"
				"characters or fewer)",
		}),
	),
	subject=(
		"Write a function that copies into dst\n"
		"$how,\n"
		"followed by a '\\0', and returns dst. n is 0 or more, and dst is large\n"
		"enough.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *dst, char *src, int n);\n"
		"\n"
		"In the examples, the line below a call shows dst after it."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}(dst, {c_string(test.args[0])}, {test.args[1]})",
	examples=(TestCase(("hello", "2")), TestCase(("hello", "9"))),
)
