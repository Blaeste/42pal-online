"""arg_pick: an original program model on the theme "use argc and argv".

The program displays one of its arguments: the first, the last, the longest
or the shortest, as it is or in upper case. The first or the last one, as
it is, gives back two real exam subjects of this theme: forbidden.
"""

from pal42.model import Exercise, Param, TestCase

def pick(args, which):
	"""Return the argument `which` asks for; on a tie, the first one."""
	if which == "first":
		return args[0]
	if which == "last":
		return args[-1]
	# max and min keep the first of several equal ones.
	if which == "longest":
		return max(args, key=len)
	return min(args, key=len)

def to_upper(text):
	"""Each lowercase ASCII letter in upper case; the rest as it is."""
	return "".join(chr(ord(char) - 32) if "a" <= char <= "z" else char for char in text)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if not test.args:
		return "\n"
	chosen = pick(test.args, params["which"])
	if params["case"] == "upper":
		chosen = to_upper(chosen)
	return chosen + "\n"

# Letters of both cases, digits, a space and symbols, for the random arguments.
ALPHABET = "abcXYZ 42!?"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random ones."""
	tests = [
		TestCase(()),
		TestCase(("only",)),
		TestCase(("a", "bb", "ccc")),
		TestCase(("ccc", "bb", "a")),
		TestCase(("same", "size", "four")),
		TestCase(("Hello", "World!", "42")),
		TestCase(("", "empty first")),
		TestCase(("x", "")),
	]
	for _ in range(10):
		count = rng.randint(1, 5)
		args = tuple(
			"".join(rng.choice(ALPHABET) for _ in range(rng.randint(0, 8)))
			for _ in range(count)
		)
		tests.append(TestCase(args))
	return tests

EXERCISE = Exercise(
	name="arg_pick",
	language="c",
	kind="program",
	assignment_name="print_${which}_${case}",
	expected_files=("print_${which}_${case}.c",),
	allowed_functions=("write",),
	themes=("pick_argument",),
	params=(
		Param("which", ("first", "last", "longest", "shortest"), {
			"first": "its first argument",
			"last": "its last argument",
			"longest": "its longest argument (the first one, if several are as long)",
			"shortest": "its shortest argument (the first one, if several are as short)",
		}),
		Param("case", ("as_is", "upper"), {
			"as_is": "as it is",
			"upper": "with each lowercase letter turned into uppercase",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that displays\n"
		"$which,\n"
		"$case,\n"
		"followed by a newline.\n"
		"\n"
		"If there is no argument, it displays only a newline."
	),
	examples=(
		TestCase(("hello", "wonderful", "world")),
		TestCase(("42",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
	# The first or the last argument, as it is: two real exam subjects.
	forbidden=(
		{"which": "first", "case": "as_is"},
		{"which": "last", "case": "as_is"},
	),
)
