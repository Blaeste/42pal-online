"""number_facts: an original program model on the theme "divisors and prime numbers".

The program takes one positive number n and displays a list about it, in
increasing order: its divisors, its prime divisors (each once), or the
prime numbers up to n, with one of three separators.
"""

from pal42.model import Exercise, Param, TestCase

# What the numbers are separated by, in the output.
SEPARATORS = {"space": " ", "comma": ", ", "newline": "\n"}

def is_prime(number):
	"""True for 2, 3, 5, 7, 11...: only 1 and itself divide it."""
	return number >= 2 and all(number % d for d in range(2, int(number ** 0.5) + 1))

def facts(n, what):
	"""The numbers `what` asks for, about n, in increasing order."""
	if what == "divisors":
		return [d for d in range(1, n + 1) if n % d == 0]
	if what == "prime_divisors":
		return [d for d in range(2, n + 1) if n % d == 0 and is_prime(d)]
	return [d for d in range(2, n + 1) if is_prime(d)]

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	# One argument, made of 1 to 6 digits only, worth more than 0.
	if len(test.args) != 1 or not test.args[0].isdigit() or len(test.args[0]) > 6:
		return "\n"
	n = int(test.args[0])
	if n == 0:
		return "\n"
	numbers = facts(n, params["what"])
	return SEPARATORS[params["separator"]].join(map(str, numbers)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random ones."""
	tests = [
		TestCase(()),
		TestCase(("1", "2")),
		TestCase(("0",)),
		TestCase(("-4",)),
		TestCase(("12a",)),
		TestCase(("1",)),
		TestCase(("13",)),
		TestCase(("360",)),
		TestCase(("007",)),
		TestCase(("1234567",)),
	]
	for _ in range(10):
		tests.append(TestCase((str(rng.randint(1, 3000)),)))
	return tests

EXERCISE = Exercise(
	name="number_facts",
	language="c",
	kind="program",
	assignment_name="${what}_${separator}",
	expected_files=("${what}_${separator}.c",),
	allowed_functions=("write",),
	themes=("prime_factors",),
	params=(
		Param("what", ("divisors", "prime_divisors", "primes_up_to"), {
			"divisors": "every divisor of n (1 and n included)",
			"prime_divisors": "every prime number that divides n, once each",
			"primes_up_to": "every prime number from 2 to n",
		}),
		Param("separator", ("space", "comma", "newline"), {
			"space": "one space",
			"comma": "a comma and a space",
			"newline": "a newline (one number per line)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one positive number n, written with 1 to 6\n"
		"digits only, and displays\n"
		"$what,\n"
		"in increasing order, separated by\n"
		"$separator, then a newline.\n"
		"\n"
		"If the number of arguments is not 1, or if the argument is not such a\n"
		"number, it displays only a newline."
	),
	examples=(
		TestCase(("12",)),
		TestCase(("1",)),
		TestCase(("4x2",)),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
