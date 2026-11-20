"""op_table: an original program model in the style of "a multiplication table".

The program takes a number n and displays a table of 5 or 9 lines: additions,
subtractions, powers or remainders with n. The multiplication table, a real
42 subject, is not one of the operations.
"""

from pal42.model import Exercise, Param, TestCase

def line(operation, n, k):
	"""Line k of the table of n."""
	if operation == "plus":
		return f"{k} + {n} = {k + n}"
	if operation == "minus":
		return f"{n} - {k} = {n - k}"
	if operation == "power":
		return f"{n} ^ {k} = {n ** k}"
	return f"{n} % {k} = {n % k}"

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1 or not test.args[0].isdigit() or not 1 <= int(test.args[0]) <= 50:
		return "\n"
	n = int(test.args[0])
	return "".join(line(params["operation"], n, k) + "\n" for k in range(1, int(params["rows"]) + 1))

def generate_tests(params, rng):
	"""Return the test cases: wrong arguments, the ends, then random numbers."""
	tests = [TestCase(args) for args in [(), ("0",), ("51",), ("x",), ("1", "2"), ("-3",)]]
	tests += [TestCase((n,)) for n in ["1", "2", "3", "7", "10", "50", "007"]]
	tests += [TestCase((str(rng.randint(1, 50)),)) for _ in range(4)]
	return tests

EXERCISE = Exercise(
	name="op_table",
	language="c",
	kind="program",
	assignment_name="table_${operation}_${rows}",
	expected_files=("table_${operation}_${rows}.c",),
	allowed_functions=("write",),
	themes=("number_table",),
	params=(
		Param("operation", ("plus", "minus", "power", "modulo"), {
			"plus": "k + n = the sum, like 1 + 3 = 4",
			"minus": "n - k = the difference, like 3 - 1 = 2 (it may be negative)",
			"power": "n ^ k = n to the power k, like 2 ^ 5 = 32",
			"modulo": "n % k = the remainder of n divided by k, like 7 % 2 = 1",
		}),
		Param("rows", ("5", "9")),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes a number n, written with digits only and from 1\n"
		"to 50, and displays a table of lines for k going from 1 to\n"
		"$rows,\n"
		"one per line, each one written as\n"
		"$operation.\n"
		"The results fit in an unsigned long long, or in a long long when negative.\n"
		"\n"
		"If the number of arguments is not 1, or if the argument is not such a\n"
		"number, the program displays only a newline."
	),
	examples=(TestCase(("3",)), TestCase(("0",))),
	oracle=oracle,
	generate_tests=generate_tests,
)
