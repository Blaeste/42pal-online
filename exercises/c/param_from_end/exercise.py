"""param_from_end: an original program model in the style of "display the last argument".

The program displays its last argument but one, or its last two arguments,
as they are, in uppercase or reversed. The last argument alone, a real 42
subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def shaped(arg, how):
	if how == "upper":
		return "".join(char.upper() if "a" <= char <= "z" else char for char in arg)
	return arg[::-1] if how == "reversed" else arg

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	args = test.args
	if len(args) < 2:
		return "\n"
	chosen = [args[-2]] if params["which"] == "second_last" else list(args[-2:])
	return " ".join(shaped(arg, params["how"]) for arg in chosen) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: too few arguments, fixed ones, then random ones."""
	tests = [TestCase(args) for args in [(), ("alone",), ("one", "two"), ("a", "Bc", "dEf"),
		("", "x", ""), ("hello world", "42!")]]
	for _ in range(6):
		tests.append(TestCase(tuple("".join(rng.choice("abXY1 ") for _ in range(rng.randint(0, 5)))
			for _ in range(rng.randint(1, 5)))))
	return tests

EXERCISE = Exercise(
	name="param_from_end",
	language="c",
	kind="program",
	assignment_name="param_${which}_${how}",
	expected_files=("param_${which}_${how}.c",),
	allowed_functions=("write",),
	themes=("last_argument",),
	params=(
		Param("which", ("second_last", "last_two"), {
			"second_last": "its last argument but one",
			"last_two": "its last two arguments, in their order, separated by one space",
		}),
		Param("how", ("plain", "upper", "reversed"), {
			"plain": "as given",
			"upper": "with their lowercase letters turned into uppercase",
			"reversed": "each one with its characters in reverse order",
		}),
	),
	subject=(
		"Write a program that displays\n"
		"$which,\n"
		"$how,\n"
		"followed by a newline.\n"
		"\n"
		"If it has fewer than 2 arguments, the program displays only a newline."
	),
	examples=(TestCase(("a", "Bc", "dEf")), TestCase(("alone",))),
	oracle=oracle,
	generate_tests=generate_tests,
)
