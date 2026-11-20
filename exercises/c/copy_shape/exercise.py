"""copy_shape: an original function model in the style of "copy a string".

The student writes a function that copies a string into a given buffer,
reversed, keeping its letters only, in uppercase, or without its spaces, and
returns the start of the buffer or the address of the \\0 it wrote there. The
plain copy, a real 42 subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def copied(src, what):
	"""What the function writes in dst, before the \\0."""
	if what == "reversed":
		return src[::-1]
	if what == "letters":
		return "".join(char for char in src if char.isascii() and char.isalpha())
	if what == "upper":
		return "".join(char.upper() if "a" <= char <= "z" else char for char in src)
	return src.replace(" ", "")

def oracle(params, test):
	"""Return what the test main prints: dst, then where the pointer returned is."""
	text = copied(test.args[0], params["what"])
	offset = len(text) if params["returned"] == "end" else 0
	return f"dst: {text}\nreturned: dst + {offset}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed strings, then random ones."""
	texts = ["hello", "", "x", "Hi 42", "a1b2 c", " a b ", "   ", "Hello, World!"]
	for _ in range(8):
		texts.append("".join(rng.choice("abXY 12-!") for _ in range(rng.randint(1, 20))))
	return [TestCase((text,)) for text in texts]

# The test main: dst is filled with X first, so that a missing \0 shows.
HARNESS = """#include <stdio.h>
#include <string.h>

char	*ft_copy_${what}_${returned}(char *dst, char *src);

int	main(int ac, char **av)
{
	char	dst[256];
	char	*returned;

	(void)ac;
	memset(dst, 'X', 255);
	dst[255] = '\\0';
	returned = ft_copy_${what}_${returned}(dst, av[1]);
	printf("dst: %s\\nreturned: dst + %ld\\n", dst, (long)(returned - dst));
	return (0);
}
"""

EXERCISE = Exercise(
	name="copy_shape",
	language="c",
	kind="function",
	assignment_name="ft_copy_${what}_${returned}",
	expected_files=("ft_copy_${what}_${returned}.c",),
	allowed_functions=(),
	themes=("string_copy",),
	params=(
		Param("what", ("reversed", "letters", "upper", "no_spaces"), {
			"reversed": "with its characters in reverse order",
			"letters": "keeping only its letters (a to z and A to Z), in their order",
			"upper": "with its lowercase letters turned into uppercase",
			"no_spaces": "without its spaces",
		}),
		Param("returned", ("start", "end"), {
			"start": "dst, the start of the copy",
			"end": "the address of the \\0 written at the end of the copy in dst",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that copies into dst the string src\n"
		"$what,\n"
		"followed by a \\0, and returns\n"
		"$returned.\n"
		"dst is always big enough.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *dst, char *src);\n"
		"\n"
		"In the examples, the lines below each call show dst after the call, and\n"
		"where the pointer returned is in dst."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}(dst, {c_string(test.args[0])})",
	examples=(TestCase(("Hello, World!",)), TestCase(("",))),
)
