"""flag_mask: an original program model in the style of "read options into
the bits of an int".

The program reads options from a to z in its arguments, kept on once given
or switched at each time, and displays them as letters, as a mask of 26
digits or as a number in hexadecimal. The real 42 subject, 32 bits in four
groups with a help option, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

LETTERS = "abcdefghijklmnopqrstuvwxyz"

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if not test.args:
		return "\n"
	mask = 0
	for arg in test.args:
		if not arg.startswith("-"):
			continue
		for char in arg[1:]:
			if char not in LETTERS:
				return "Bad option\n"
			bit = 1 << LETTERS.index(char)
			mask = mask | bit if params["repeat"] == "set" else mask ^ bit
	on = [mask >> index & 1 for index in range(26)]
	if params["show"] == "letters":
		return "".join(letter for letter, bit in zip(LETTERS, on) if bit) + "\n"
	if params["show"] == "mask":
		return "".join(str(bit) for bit in on) + "\n"
	return f"{mask:x}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed arguments first, then random ones."""
	tests = [
		TestCase(()), TestCase(("-",)), TestCase(("word",)), TestCase(("-ab", "-z", "x", "-a")),
		TestCase(("-a1",)), TestCase(("-b", "-A")), TestCase(("--a",)), TestCase(("-aa", "-")),
		TestCase(("-abcdefghijklmnopqrstuvwxyz",)), TestCase(("-zyx", "zz", "-x")),
		TestCase(("a-b", "-c")), TestCase(("-p", "-q", "-", "-p", "-p")),
	]
	for _ in range(10):
		args = []
		for _ in range(rng.randint(1, 4)):
			body = "".join(rng.choice("abcxyz") for _ in range(rng.randint(0, 4)))
			if rng.randint(0, 9) == 0:
				body += rng.choice("A1 _")
			args.append(("-" if rng.randint(0, 4) else "") + body)
		tests.append(TestCase(tuple(args)))
	return tests

EXERCISE = Exercise(
	name="flag_mask",
	language="c",
	kind="program",
	assignment_name="flags_${show}_${repeat}",
	expected_files=("flags_${show}_${repeat}.c",),
	allowed_functions=("write",),
	themes=("option_flags",),
	params=(
		Param("show", ("letters", "mask", "hex"), {
			"letters": "the options that are on, as their letters in alphabetical order (nothing\n"
				"if none is on)",
			"mask": "26 digits, one for each letter from a to z in this order: 1 if its\n"
				"option is on, 0 otherwise",
			"hex": "a number in hexadecimal (in lower case, with no zeros in front, 0 if no\n"
				"option is on) whose bit 0 is 1 if the option a is on, bit 1 if b is on,\n"
				"and so on up to bit 25 for z",
		}),
		Param("repeat", ("set", "toggle"), {
			"set": "turns it on; an option given again stays on",
			"toggle": "switches it: on if it was off, off if it was on",
		}),
	),
	subject=(
		"Write a program that reads options in its arguments and displays them.\n"
		"\n"
		"An argument that starts with - holds options: each character after the - is\n"
		"one option, a lowercase letter from a to z. The other arguments are ignored.\n"
		"All the options are off at the start, and each option given\n"
		"$repeat.\n"
		"\n"
		"The program then displays\n"
		"$show,\n"
		"followed by a newline.\n"
		"\n"
		"If a character of an option is not a lowercase letter, the program\n"
		"displays Bad option followed by a newline, and nothing else.\n"
		"\n"
		"If there is no argument, the program displays a newline."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	examples=(TestCase(("-ab", "-z", "x", "-a")), TestCase(("-p", "-q", "-", "-p", "-p")),
		TestCase(("-a1",)), TestCase(())),
)
