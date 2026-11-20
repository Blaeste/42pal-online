"""char_line: an original program model in the style of "display one character".

The program displays a line of 5 or 10 times the same character, #, - or =,
followed by a newline. One z, a real 42 subject, is not one of the lines.
"""

from pal42.model import Exercise, Param, TestCase

CHARS = {"hash": "#", "dash": "-", "equal": "="}

def oracle(params, test):
	"""Return what the program prints, whatever its arguments."""
	return CHARS[params["char"]] * int(params["count"]) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: no argument, then arguments that change nothing."""
	return [TestCase(()), TestCase(("10",)), TestCase(("a", "b"))]

EXERCISE = Exercise(
	name="char_line",
	language="c",
	kind="program",
	assignment_name="line_${char}_${count}",
	expected_files=("line_${char}_${count}.c",),
	allowed_functions=("write",),
	themes=("one_char_end",),
	params=(
		Param("char", ("hash", "dash", "equal"), {
			"hash": "the character #",
			"dash": "the character -",
			"equal": "the character =",
		}),
		Param("count", ("5", "10")),
	),
	subject=(
		"Write a program that displays a line made of\n"
		"$count\n"
		"times\n"
		"$char,\n"
		"followed by a newline.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
