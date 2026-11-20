"""byte_dump: an original function model in the style of "display an area
of memory in hexadecimal".

The student writes a function that displays the bytes found at an address,
8 or 12 per line, each line starting with its offset, or followed by the
bytes as text. The real 42 subject, 16 bytes per line in groups of two, is
not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

WIDTHS = {"eight": 8, "twelve": 12}

def dump(data, layout, width):
	"""The lines displayed for the bytes of `data` (a str of ASCII characters)."""
	size = WIDTHS[width]
	lines = []
	for start in range(0, len(data), size):
		chunk = data[start:start + size]
		if layout == "offset":
			lines.append(f"{start:04x}:" + "".join(f" {ord(char):02x}" for char in chunk) + "\n")
		else:
			cells = "".join(f"{ord(char):02x} " for char in chunk).ljust(3 * size)
			text = "".join(char if " " <= char <= "~" else "." for char in chunk)
			lines.append(f"{cells}|{text}|\n")
	return "".join(lines)

def oracle(params, test):
	"""Return what the test main prints: the dump of the bytes of av[1]."""
	return dump(test.args[0], params["layout"], params["width"])

def c_bytes(text):
	"""Write text as a C string, the characters that cannot be printed as \\ooo."""
	escapes = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\t": "\\t"}
	return '"' + "".join(escapes.get(char) or (char if " " <= char <= "~" else f"\\{ord(char):03o}")
		for char in text) + '"'

def generate_tests(params, rng):
	"""Return the test cases: fixed strings first, then random ones of ASCII bytes."""
	texts = ["", "A", "Hello, 42!", "abcdefghijklmnopq", "a\tb\x7f", "line one\nline two\n",
		"exactly8", "exactly twelve..", "\x01\x02\x03 ~", "x" * 25]
	for _ in range(8):
		length = rng.randint(1, 30)
		texts.append("".join(rng.choice("az 9~.\t") if rng.randint(0, 3) else chr(rng.randint(1, 127))
			for _ in range(length)))
	return [TestCase((text,)) for text in texts]

# The test main: it hands the function the bytes of av[1], without the '\0'.
HARNESS = """#include <string.h>

void	ft_dump_${layout}_${width}(const void *addr, size_t size);

int	main(int ac, char **av)
{
	(void)ac;
	ft_dump_${layout}_${width}(av[1], strlen(av[1]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="byte_dump",
	language="c",
	kind="function",
	assignment_name="ft_dump_${layout}_${width}",
	expected_files=("ft_dump_${layout}_${width}.c",),
	allowed_functions=("write",),
	themes=("memory_dump",),
	params=(
		Param("layout", ("offset", "text"), {
			"offset": "the offset of its first byte from addr, in hexadecimal on 4 digits (with\n"
				"zeros in front), then a colon, then each of its bytes as a space followed\n"
				"by its 2 hexadecimal digits.",
			"text": "two parts:\n"
				"- its bytes, each as its 2 hexadecimal digits followed by a space (the\n"
				"last line gets 3 spaces for each byte it lacks, so that the columns line\n"
				"up);\n"
				"- the same bytes as text, between two |: a printable byte (from space to\n"
				"~) as itself, any other one as a dot.",
		}),
		Param("width", ("eight", "twelve"), {"eight": "8", "twelve": "12"}),
	),
	subject=(
		"Write a function that displays the size bytes found at the address addr,\n"
		"$width bytes per line (the last line may have fewer). Each line shows\n"
		"$layout\n"
		"\n"
		"A newline ends each line. The hexadecimal digits are written in lower\n"
		"case. If size is 0, the function displays nothing.\n"

		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(const void *addr, size_t size);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_bytes(test.args[0])}, {len(test.args[0])})",
	examples=(TestCase(("Hello, 42!",)), TestCase(("a\tb\x7f",)), TestCase(("abcdefghijklmnopq",))),
)
