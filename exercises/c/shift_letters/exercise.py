"""shift_letters: an original model on the theme "transform each character".

The program gets one string and prints it with some letters shifted in the
alphabet. The variants change how far (2, 3 or 5 positions), in which
direction, and which letters move. Shifts of 1 and 13 are left out on
purpose: they would give back two real exam subjects of this theme.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	step = int(params["shift"])
	# Backward is a negative step; % 26 in shift_char brings it back into
	# the alphabet (in Python, -3 % 26 is 23).
	if params["direction"] == "backward":
		step = -step
	letters = params["letters"]
	return "".join(shift_char(char, step, letters) for char in test.args[0]) + "\n"

def shift_char(char, step, letters):
	"""Return `char` moved `step` letters (negative: backward), if it must move.

	letters says which ones move: "all", "lowercase" or "uppercase".
	"""
	if "a" <= char <= "z" and letters in ("all", "lowercase"):
		return chr((ord(char) - ord("a") + step) % 26 + ord("a"))
	if "A" <= char <= "Z" and letters in ("all", "uppercase"):
		return chr((ord(char) - ord("A") + step) % 26 + ord("A"))
	return char

# Letters of both cases, with the ends of the alphabet, plus other characters
# that must not move.
ALPHABET = "abcxyzABCXYZhello WORLD 0189!?,."

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random ones.

	The same rng (same seed) gives the same tests. They do not depend on
	params: every variant is graded on the same arguments.
	"""
	tests = [
		# Wrong number of arguments.
		TestCase(()),
		TestCase(("one", "two")),
		# An empty string, the ends of the alphabet, no letter at all.
		TestCase(("",)),
		TestCase(("az AZ",)),
		TestCase(("abcdefghijklmnopqrstuvwxyz",)),
		TestCase(("ABCDEFGHIJKLMNOPQRSTUVWXYZ",)),
		TestCase(("42 !?",)),
		TestCase(("Hello, World!",)),
	]
	for _ in range(10):
		length = rng.randint(0, 20)
		tests.append(TestCase(("".join(rng.choice(ALPHABET) for _ in range(length)),)))
	return tests

EXERCISE = Exercise(
	name="shift_letters",
	language="c",
	kind="program",
	assignment_name="${direction}_shift_${shift}",
	expected_files=("${direction}_shift_${shift}.c",),
	allowed_functions=("write",),
	themes=("letter_rotation",),
	params=(
		Param("shift", ("2", "3", "5"), {
			"2": "2 positions",
			"3": "3 positions",
			"5": "5 positions",
		}),
		Param("direction", ("forward", "backward"), {
			"forward": "forward in the alphabet",
			"backward": "backward in the alphabet",
		}),
		Param("letters", ("all", "lowercase", "uppercase"), {
			"all": "every letter",
			"lowercase": "every lowercase letter",
			"uppercase": "every uppercase letter",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters
	# whatever the texts put in them.
	subject=(
		"This program receives one string and prints it with $letters\n"
		"shifted by $shift, $direction.\n"
		"The shift wraps around the alphabet: after z comes a, and before a comes z\n"
		"(the same for Z and A).\n"
		"Every other character is printed as it is, and a newline ends the line.\n"
		"\n"
		"With any other number of arguments, it prints only a newline."
	),
	examples=(
		TestCase(("abc xyz",)),
		TestCase(("Hello, World!",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
