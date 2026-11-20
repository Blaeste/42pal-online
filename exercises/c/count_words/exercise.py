"""count_words: an original program model in the style of "count, with words
for some numbers".

The program counts from 1 up to the number it is given, one number a line,
writing bip for the multiples of a number, bop for the numbers that hold a
digit or end with one, and bipbop for both. The multiples of 3 and 5 up to
100, the real 42 subject, are not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

BIPS = {"by3": 3, "by4": 4}
BOPS = {"has7": lambda n: "7" in str(n), "has2": lambda n: "2" in str(n), "ends5": lambda n: n % 10 == 5}

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	lines = []
	for n in range(1, int(test.args[0]) + 1):
		word = ("bip" if n % BIPS[params["bip"]] == 0 else "") + ("bop" if BOPS[params["bop"]](n) else "")
		lines.append(word or str(n))
	return "".join(line + "\n" for line in lines)

def generate_tests(params, rng):
	tests = [TestCase(()), TestCase(("15",)), TestCase(("20",)), TestCase(("1",)), TestCase(("100",)),
		TestCase(("27",)), TestCase(("1", "2"))]
	tests += [TestCase((str(rng.randint(2, 100)),)) for _ in range(5)]
	return tests

EXERCISE = Exercise(
	name="count_words",
	language="c",
	kind="program",
	assignment_name="words_${bip}_${bop}",
	expected_files=("words_${bip}_${bop}.c",),
	allowed_functions=("write",),
	themes=("number_words",),
	params=(
		Param("bip", ("by3", "by4"), {"by3": "3", "by4": "4"}),
		Param("bop", ("has7", "has2", "ends5"), {
			"has7": "that hold the digit 7 (7, 17, 70...)",
			"has2": "that hold the digit 2 (2, 12, 20...)",
			"ends5": "that end with the digit 5 (5, 15, 25...)",
		}),
	),
	subject=(
		"Write a program that takes a number from 1 to 100 and displays the numbers\n"
		"from 1 up to it, one a line, each followed by a newline, except that:\n"
		"\n"
		"- the multiples of $bip are replaced by bip;\n"
		"- the numbers $bop are replaced by bop;\n"
		"- the numbers that are both are replaced by bipbop.\n"
		"\n"
		"If the number of arguments is not 1, the program displays a newline."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	examples=(TestCase(("15",)), TestCase(())),
)
