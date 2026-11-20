"""count_down: an original program model in the style of "a countdown of the digits".

The program counts down from 5, 7 or 12 to 0, the numbers separated by
spaces or by commas, followed by a newline. The digits from 9 to 0 joined,
a real 42 subject, are not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

SEPARATORS = {"space": " ", "comma": ", "}

def oracle(params, test):
	"""Return what the program prints, whatever its arguments."""
	numbers = range(int(params["start"]), -1, -1)
	return SEPARATORS[params["separator"]].join(map(str, numbers)) + "\n"

def generate_tests(params, rng):
	return [TestCase(()), TestCase(("9",)), TestCase(("a", "b"))]

EXERCISE = Exercise(
	name="count_down",
	language="c",
	kind="program",
	assignment_name="countdown_${start}_${separator}",
	expected_files=("countdown_${start}_${separator}.c",),
	allowed_functions=("write",),
	themes=("digit_countdown",),
	params=(
		Param("start", ("5", "7", "12")),
		Param("separator", ("space", "comma"), {
			"space": "one space",
			"comma": "a comma and a space",
		}),
	),
	subject=(
		"Write a program that displays the numbers from\n"
		"$start\n"
		"down to 0, in decreasing order, separated by\n"
		"$separator,\n"
		"followed by a newline.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
