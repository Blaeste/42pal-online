"""base_print: an original program model on the theme "print an integer in another base".

The program takes a positive number written in base 10 and displays it in
binary, octal or hexadecimal: as it is, after a prefix (0b, 0o, 0x), or in
groups of 4 digits. Hexadecimal as it is gives back a real 42 subject: it
is left out.
"""

from pal42.model import Exercise, Param, TestCase

# The format letter of Python's format() and the prefix of each base.
BASES = {"binary": ("b", "0b"), "octal": ("o", "0o"), "hex": ("x", "0x")}

def grouped(digits):
	"""The digits in groups of 4 counted from the right: 1 0000 0000."""
	first = len(digits) % 4 or 4
	groups = [digits[:first]]
	groups += [digits[i:i + 4] for i in range(first, len(digits), 4)]
	return " ".join(groups)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	letter, prefix = BASES[params["base"]]
	digits = format(int(test.args[0]), letter)
	if params["form"] == "prefixed":
		return prefix + digits + "\n"
	if params["form"] == "grouped":
		return grouped(digits) + "\n"
	return digits + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random numbers."""
	tests = [TestCase(()), TestCase(("1", "2"))]
	numbers = ["0", "1", "007", "15", "16", "255", "256", "4096", "2147483647"]
	numbers += [str(rng.randint(0, 2**31 - 1)) for _ in range(6)]
	numbers += [str(rng.randint(0, 5000)) for _ in range(4)]
	return tests + [TestCase((number,)) for number in numbers]

EXERCISE = Exercise(
	name="base_print",
	language="c",
	kind="program",
	assignment_name="to_${base}_${form}",
	expected_files=("to_${base}_${form}.c",),
	allowed_functions=("write",),
	themes=("print_in_base",),
	params=(
		Param("base", ("binary", "octal", "hex"), {
			"binary": "in binary (base 2)",
			"octal": "in octal (base 8)",
			"hex": "in hexadecimal (base 16, with the lowercase letters a to f)",
		}),
		Param("form", ("plain", "prefixed", "grouped"), {
			"plain": "The digits are displayed as they are",
			"prefixed": "The digits come after a prefix: 0b, 0o or 0x for bases 2, 8 and 16",
			"grouped": "The digits are displayed in groups of 4, counted from the right and\n"
				"separated by one space (the first group may be shorter)",
		}),
	),
	# print_hex is a real subject.
	forbidden=({"base": "hex", "form": "plain"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one positive number, written in base 10, and\n"
		"displays it\n"
		"$base,\n"
		"followed by a newline.\n"
		"$form.\n"
		"\n"
		"The number is always made of digits only, and fits in an int.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	examples=(
		TestCase(("42",)),
		TestCase(("4096",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
