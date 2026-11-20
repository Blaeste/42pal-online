"""bip_bop: an original program model in the style of "count and replace multiples by words".

The program displays the numbers from 1 to 30 or 50, one per line, the
multiples of a first number replaced by bip, of a second by bop, and of both
by bipbop. 3 and 5 up to 100 give back a real 42 subject: they are never a
pair of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program prints: one line per number."""
	first, second = map(int, params["pair"].split("_"))
	out = ""
	for n in range(1, int(params["upto"]) + 1):
		word = ("bip" if n % first == 0 else "") + ("bop" if n % second == 0 else "")
		out += (word or str(n)) + "\n"
	return out

def generate_tests(params, rng):
	"""Return the test cases: no argument, then arguments that change nothing."""
	return [TestCase(()), TestCase(("12",)), TestCase(("a", "b"))]

EXERCISE = Exercise(
	name="bip_bop",
	language="c",
	kind="program",
	assignment_name="bipbop_${pair}_${upto}",
	expected_files=("bipbop_${pair}_${upto}.c",),
	allowed_functions=("write",),
	themes=("number_words",),
	params=(
		Param("pair", ("2_7", "3_4", "4_6", "5_7"), {
			"2_7": "2 by bip, the multiples of 7 by bop, and the multiples of both by bipbop",
			"3_4": "3 by bip, the multiples of 4 by bop, and the multiples of both by bipbop",
			"4_6": "4 by bip, the multiples of 6 by bop, and the multiples of both by bipbop",
			"5_7": "5 by bip, the multiples of 7 by bop, and the multiples of both by bipbop",
		}),
		Param("upto", ("30", "50")),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that displays the numbers from 1 to\n"
		"$upto,\n"
		"one per line, replacing the multiples of\n"
		"$pair.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
