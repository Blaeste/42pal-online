"""arg_measure: an original program model in the style of "count the arguments".

The program displays a number about its arguments: the sum of their
lengths, the length of the longest one, how many are numbers, or how many
are different. The number of arguments, a real 42 subject, is not one of
the variants.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	args = test.args
	what = params["what"]
	if what == "total_length":
		result = sum(len(arg) for arg in args)
	elif what == "longest":
		result = max((len(arg) for arg in args), default=0)
	elif what == "numbers":
		result = sum(1 for arg in args if arg.isdigit() and arg.isascii())
	else:
		result = len(set(args))
	return f"{result}\n"

def generate_tests(params, rng):
	"""Return the test cases: no argument, fixed ones, then random ones."""
	tests = [TestCase(args) for args in [(), ("",), ("ab", "cde", ""), ("12", "x1", "007", ""),
		("a", "b", "a", ""), ("same", "same", "same"), ("-5", "+5", "5")]]
	for _ in range(8):
		tests.append(TestCase(tuple("".join(rng.choice("ab12") for _ in range(rng.randint(0, 3)))
			for _ in range(rng.randint(1, 7)))))
	return tests

EXERCISE = Exercise(
	name="arg_measure",
	language="c",
	kind="program",
	assignment_name="args_${what}",
	expected_files=("args_${what}.c",),
	allowed_functions=("write",),
	themes=("argument_count",),
	params=(
		Param("what", ("total_length", "longest", "numbers", "distinct"), {
			"total_length": "the sum of the lengths of its arguments",
			"longest": "the length of its longest argument",
			"numbers": "how many of its arguments are numbers: made of digits only, and not\n"
				"empty (a sign is not a digit)",
			"distinct": "how many different arguments it has (the same string twice counts\n"
				"once)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that displays\n"
		"$what,\n"
		"followed by a newline. With no argument, it displays 0 followed by a\n"
		"newline."
	),
	examples=(TestCase(("ab", "cde", "")), TestCase(("12", "x1", "007")), TestCase(())),
	oracle=oracle,
	generate_tests=generate_tests,
)
