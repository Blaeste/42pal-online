"""prime_facts: an original program model in the style of "add up prime numbers".

The program takes a positive number n and displays how many prime numbers
there are, the largest one, or the sum of their digits, from 2 to n or from
n to 2n. The sum of the prime numbers up to n, a real 42 subject, is not
one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def is_prime(number):
	return number >= 2 and all(number % d for d in range(2, int(number ** 0.5) + 1))

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1 or not test.args[0].isdigit() or int(test.args[0]) == 0:
		return "0\n"
	n = int(test.args[0])
	low, high = (2, n) if params["range"] == "up_to" else (n, 2 * n)
	found = [p for p in range(low, high + 1) if is_prime(p)]
	if params["measure"] == "count":
		return f"{len(found)}\n"
	if params["measure"] == "largest":
		return f"{found[-1] if found else 0}\n"
	return f"{sum(int(digit) for p in found for digit in str(p))}\n"

def generate_tests(params, rng):
	"""Return the test cases: wrong arguments, small numbers, then random ones."""
	numbers = ["1", "2", "3", "10", "13", "100", "997", "20000"]
	tests = [TestCase(()), TestCase(("0",)), TestCase(("-5",)), TestCase(("12a",)), TestCase(("1", "2"))]
	tests += [TestCase((n,)) for n in numbers]
	tests += [TestCase((str(rng.randint(1, 5000)),)) for _ in range(6)]
	return tests

EXERCISE = Exercise(
	name="prime_facts",
	language="c",
	kind="program",
	assignment_name="primes_${measure}_${range}",
	expected_files=("primes_${measure}_${range}.c",),
	allowed_functions=("write",),
	themes=("prime_sum",),
	params=(
		Param("measure", ("count", "largest", "digit_sum"), {
			"count": "how many prime numbers there are",
			"largest": "the largest prime number (0 if there is none)",
			"digit_sum": "the sum of all the digits of the prime numbers (13 gives 1 + 3)",
		}),
		Param("range", ("up_to", "between"), {
			"up_to": "from 2 to n",
			"between": "from n to 2n (n and 2n included)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes a positive number n, written with digits only,\n"
		"and displays\n"
		"$measure,\n"
		"$range,\n"
		"followed by a newline. n is never more than 20000.\n"
		"\n"
		"If the number of arguments is not 1, or if the argument is not a positive\n"
		"number, the program displays 0 followed by a newline."
	),
	examples=(TestCase(("10",)), TestCase(("1",)), TestCase(())),
	oracle=oracle,
	generate_tests=generate_tests,
)
