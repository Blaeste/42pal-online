"""alpha_back: an original program model in the style of "display the alphabet backwards".

The program displays the alphabet from z to a, every letter or one out of
two, with a pattern of case: alternating (lowercase or uppercase first),
one letter in three in uppercase, or the first half in uppercase. Every
letter, alternating with lowercase first, gives back a real 42 subject: it
is left out.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program prints: the letters from z to a, then a newline."""
	letters = "zyxwvutsrqponmlkjihgfedcba"
	if params["step"] == "skip":
		letters = letters[::2]
	shown = []
	for place, letter in enumerate(letters):
		pattern = params["pattern"]
		if pattern == "alternate_lower":
			upper = place % 2 == 1
		elif pattern == "alternate_upper":
			upper = place % 2 == 0
		elif pattern == "thirds":
			upper = place % 3 == 0
		else:
			upper = letter >= "n"
		shown.append(letter.upper() if upper else letter)
	return "".join(shown) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: no argument, then arguments that change nothing."""
	return [TestCase(()), TestCase(("abc",)), TestCase(("1", "2"))]

EXERCISE = Exercise(
	name="alpha_back",
	language="c",
	kind="program",
	assignment_name="alpha_back_${pattern}_${step}",
	expected_files=("alpha_back_${pattern}_${step}.c",),
	allowed_functions=("write",),
	themes=("backward_alphabet",),
	params=(
		Param("pattern", ("alternate_lower", "alternate_upper", "thirds", "halves"), {
			"alternate_lower": "one letter out of two is in uppercase, starting with the second\n"
				"one shown (the first one is in lowercase)",
			"alternate_upper": "one letter out of two is in uppercase, starting with the first\n"
				"one shown",
			"thirds": "one letter out of three is in uppercase, starting with the first\n"
				"one shown",
			"halves": "the letters from z to n are in uppercase, the letters from m to a in\n"
				"lowercase",
		}),
		Param("step", ("all", "skip"), {
			"all": "every letter, from z to a",
			"skip": "one letter out of two: z, x, v and so on down to b",
		}),
	),
	# Every letter, alternating with lowercase first: a real subject.
	forbidden=({"pattern": "alternate_lower", "step": "all"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that displays the letters of the alphabet backwards,\n"
		"$step,\n"
		"followed by a newline. Among the letters shown,\n"
		"$pattern.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
