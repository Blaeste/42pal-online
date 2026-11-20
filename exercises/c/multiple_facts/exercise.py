"""multiple_facts: an original program model in the style of "the least common multiple".

The program takes 2 to 5 positive numbers and displays their least common
multiple, their first three common multiples, how many common multiples
there are up to 1000, or the first one over 100. The real 42 subject is a
function that returns the least common multiple of two numbers.
"""

from math import gcd

from pal42.model import Exercise, Param, TestCase

def is_number(text):
	return text.isdigit() and 1 <= int(text) <= 1000

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if not 2 <= len(test.args) <= 5 or not all(is_number(arg) for arg in test.args):
		return "\n"
	lcm = 1
	for arg in test.args:
		lcm = lcm * int(arg) // gcd(lcm, int(arg))
	what = params["what"]
	if what == "lcm_all":
		return f"{lcm}\n"
	if what == "first_three":
		return f"{lcm} {2 * lcm} {3 * lcm}\n"
	if what == "count_up_to_1000":
		return f"{1000 // lcm}\n"
	return f"{(100 // lcm + 1) * lcm}\n"

def generate_tests(params, rng):
	"""Return the test cases: wrong arguments, fixed numbers, then random ones."""
	tests = [TestCase(args) for args in [(), ("4",), ("4", "0"), ("4", "x"), ("4", "1001"), ("1",) * 6]]
	for args in [("4", "6"), ("2", "3", "4"), ("7", "11", "13"), ("1", "1"), ("100", "100"),
			("997", "991", "983", "977", "971"), ("50", "4")]:
		tests.append(TestCase(args))
	for _ in range(6):
		tests.append(TestCase(tuple(str(rng.randint(1, 60)) for _ in range(rng.randint(2, 4)))))
	return tests

EXERCISE = Exercise(
	name="multiple_facts",
	language="c",
	kind="program",
	assignment_name="multiples_${what}",
	expected_files=("multiples_${what}.c",),
	allowed_functions=("write",),
	themes=("common_multiple",),
	params=(
		Param("what", ("lcm_all", "first_three", "count_up_to_1000", "next_after_100"), {
			"lcm_all": "their least common multiple: the smallest number they all divide",
			"first_three": "their first three common multiples, in increasing order, separated\n"
				"by spaces",
			"count_up_to_1000": "how many common multiples they have from 1 to 1000",
			"next_after_100": "their smallest common multiple greater than 100",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes 2 to 5 numbers, each one written with digits\n"
		"only and from 1 to 1000, and displays\n"
		"$what,\n"
		"followed by a newline. The results fit in an unsigned long long.\n"
		"\n"
		"If there are not 2 to 5 arguments, or if one of them is not such a number,\n"
		"the program displays only a newline."
	),
	examples=(TestCase(("4", "6")), TestCase(("7", "11", "13")), TestCase(("4",))),
	oracle=oracle,
	generate_tests=generate_tests,
)
