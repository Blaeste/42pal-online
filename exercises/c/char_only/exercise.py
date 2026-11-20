"""char_only: an original program model in the style of "display one character".

The program displays one fixed character, e, k, x or 7, with or without a
newline after it. The characters a and z, real 42 subjects, are never the
one displayed.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program prints, whatever its arguments."""
	return params["char"] + ("\n" if params["end"] == "newline" else "")

def generate_tests(params, rng):
	"""Return the test cases: no argument, then arguments that change nothing."""
	return [TestCase(()), TestCase(("a",)), TestCase(("z", "x"))]

EXERCISE = Exercise(
	name="char_only",
	language="c",
	kind="program",
	assignment_name="only_${char}_${end}",
	expected_files=("only_${char}_${end}.c",),
	allowed_functions=("write",),
	themes=("one_char",),
	params=(
		Param("char", ("e", "k", "x", "7")),
		Param("end", ("bare", "newline"), {
			"bare": "with nothing after it (no newline)",
			"newline": "followed by a newline",
		}),
	),
	subject=(
		"Write a program that displays the character\n"
		"$char\n"
		"on the standard output,\n"
		"$end.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
