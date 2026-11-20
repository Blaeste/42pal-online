"""divisor_facts: an original program model in the style of "the greatest common divisor".

The program takes two positive numbers and displays how many divisors they
have in common, the list of them, whether they are coprime, or the steps of
Euclid's algorithm. The greatest common divisor alone, a real 42 subject,
is not one of the variants.
"""

from math import gcd

from pal42.model import Exercise, Param, TestCase

def is_number(text):
	return text.isdigit() and len(text) <= 7 and int(text) > 0

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 2 or not all(is_number(arg) for arg in test.args):
		return "\n"
	a, b = int(test.args[0]), int(test.args[1])
	what = params["what"]
	common = [d for d in range(1, gcd(a, b) + 1) if gcd(a, b) % d == 0]
	if what == "common_count":
		return f"{len(common)}\n"
	if what == "common_list":
		return " ".join(map(str, common)) + "\n"
	if what == "coprime":
		return ("yes" if gcd(a, b) == 1 else "no") + "\n"
	steps = [a, b]
	while steps[-2] % steps[-1]:
		steps.append(steps[-2] % steps[-1])
	return " ".join(map(str, steps)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: wrong arguments, fixed pairs, then random ones."""
	tests = [TestCase(args) for args in [(), ("4",), ("4", "0"), ("4", "x"), ("1", "2", "3")]]
	for pair in [("12", "18"), ("7", "9"), ("48", "18"), ("1", "1"), ("100", "75"), ("17", "34"),
			("1000000", "999999")]:
		tests.append(TestCase(pair))
	for _ in range(6):
		tests.append(TestCase((str(rng.randint(1, 3000)), str(rng.randint(1, 3000)))))
	return tests

EXERCISE = Exercise(
	name="divisor_facts",
	language="c",
	kind="program",
	assignment_name="divisors_${what}",
	expected_files=("divisors_${what}.c",),
	allowed_functions=("write",),
	themes=("common_divisor",),
	params=(
		Param("what", ("common_count", "common_list", "coprime", "euclid_steps"), {
			"common_count": "how many divisors they have in common",
			"common_list": "the divisors they have in common, in increasing order, separated by\n"
				"spaces",
			"coprime": "yes if their only common divisor is 1, no otherwise",
			"euclid_steps": "the steps of Euclid's algorithm, separated by spaces. They start with\n"
				"the two numbers; then each next number is the one before the last modulo\n"
				"the last one, as long as it is not 0 (48 18 gives 48 18 12 6)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes two positive numbers, written with digits only\n"
		"(at most 7 of them), and displays\n"
		"$what,\n"
		"followed by a newline.\n"
		"\n"
		"If the number of arguments is not 2, or if one of them is not such a\n"
		"number, the program displays only a newline."
	),
	examples=(TestCase(("12", "18")), TestCase(("7", "9")), TestCase(("4",))),
	oracle=oracle,
	generate_tests=generate_tests,
)
