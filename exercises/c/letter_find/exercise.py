"""letter_find: an original program model in the style of "display the first letter a".

The program displays the first e, o or s of a string (in the exact case, or
in either case), or only a newline if there is none; without exactly one
argument, it displays the letter. The letters a and z, real 42 subjects,
are never the letter looked for.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	letter = params["letter"]
	if len(test.args) != 1:
		return letter + "\n"
	for char in test.args[0]:
		if char == letter or (params["case"] == "any_case" and char.lower() == letter):
			return char + "\n"
	return "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",))]
	for text in ["Hello", "HELLO", "Ostrich SOS", "nothing here", "seashore", "E O S e o s"]:
		tests.append(TestCase((text,)))
	for _ in range(6):
		tests.append(TestCase(("".join(rng.choice("abeEoOsS x") for _ in range(rng.randint(1, 10))),)))
	return tests

EXERCISE = Exercise(
	name="letter_find",
	language="c",
	kind="program",
	assignment_name="show_${letter}_${case}",
	expected_files=("show_${letter}_${case}.c",),
	allowed_functions=("write",),
	themes=("letter_search",),
	params=(
		Param("letter", ("e", "o", "s")),
		Param("case", ("exact", "any_case"), {
			"exact": "in lowercase only",
			"any_case": "in lowercase or in uppercase (the one found is displayed)",
		}),
	),
	subject=(
		"Write a program that takes one string and displays the first letter\n"
		"$letter\n"
		"it finds in it,\n"
		"$case,\n"
		"followed by a newline. If there is none, it displays only a newline.\n"
		"\n"
		"If the number of arguments is not 1, the program displays the letter\n"
		"$letter\n"
		"followed by a newline."
	),
	examples=(TestCase(("Hello World",)), TestCase(("nothing",)), TestCase(())),
	oracle=oracle,
	generate_tests=generate_tests,
)
