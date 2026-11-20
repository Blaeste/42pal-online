"""merge_chars: an original program model in the style of "the characters of two strings".

The program displays, without doubles, the characters of two strings: all
of them, those found in only one of the two, or their letters only, in the
order they appear or in ASCII order, up or down. All of them in the order
they appear, a real 42 subject, is left out.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 2:
		return "\n"
	first, second = test.args
	chars = []
	for char in first + second:
		if char in chars:
			continue
		if params["which"] == "once" and (char in first) == (char in second):
			continue
		if params["which"] == "letters" and not (char.isascii() and char.isalpha()):
			continue
		chars.append(char)
	if params["order"] != "appearance":
		chars.sort(reverse=params["order"] == "reverse_ascii")
	return "".join(chars) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed pairs, then random ones."""
	tests = [TestCase(()), TestCase(("a",)), TestCase(("a", "b", "c")), TestCase(("", ""))]
	for pair in [("hello", "world"), ("ab1", "BA2!"), ("a-a", "--"), ("same", "same"),
			("", "abc"), ("Zz yY", "y z!")]:
		tests.append(TestCase(pair))
	for _ in range(8):
		tests.append(TestCase(tuple("".join(rng.choice("abcABC 12-!") for _ in range(rng.randint(0, 10)))
			for _ in range(2))))
	return tests

EXERCISE = Exercise(
	name="merge_chars",
	language="c",
	kind="program",
	assignment_name="merge_${which}_${order}",
	expected_files=("merge_${which}_${order}.c",),
	allowed_functions=("write",),
	themes=("merged_chars",),
	params=(
		Param("which", ("all", "once", "letters"), {
			"all": "found in at least one of them",
			"once": "found in only one of them (not in both)",
			"letters": "found in at least one of them that are letters (a to z, A to Z)",
		}),
		Param("order", ("appearance", "ascii", "reverse_ascii"), {
			"appearance": "in the order they appear in the first string, then in the second",
			"ascii": "in increasing ASCII order",
			"reverse_ascii": "in decreasing ASCII order",
		}),
	),
	# All of them, in the order they appear: a real subject.
	forbidden=({"which": "all", "order": "appearance"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes two strings and displays, without doubles, the\n"
		"characters\n"
		"$which,\n"
		"$order,\n"
		"followed by a newline.\n"
		"\n"
		"If the number of arguments is not 2, the program displays only a newline."
	),
	examples=(
		TestCase(("hello", "world")),
		TestCase(("Zz yY", "y z!")),
		TestCase(("a",)),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
