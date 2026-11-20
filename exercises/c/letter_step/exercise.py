"""letter_step: an original program model in the style of "move each letter one step".

The program moves some characters of a string one step: each vowel to the
next vowel, each consonant to the next consonant, each digit to the next
digit, or each letter to the one before; the characters moved may also
change case. Every letter to the next one, a real 42 subject, is not one of
the variants.
"""

from pal42.model import Exercise, Param, TestCase

# Each group, in order: a character moves to the next one, the last to the first.
GROUPS = {
	"vowels": "aeiou",
	"consonants": "bcdfghjklmnpqrstvwxyz",
	"digits": "0123456789",
	"backward_letters": "zyxwvutsrqponmlkjihgfedcba",
}

def step(char, what):
	"""The character after `char` in the group of `what`, or None if it does not move."""
	group = GROUPS[what]
	lower = char.lower() if char.isascii() else char
	if lower not in group:
		return None
	after = group[(group.index(lower) + 1) % len(group)]
	return after.upper() if char.isupper() else after

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	result = ""
	for char in test.args[0]:
		moved = step(char, params["what"])
		if moved is None:
			result += char
		else:
			result += moved.swapcase() if params["case"] == "swap" else moved
	return result + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",))]
	for text in ["Hello World", "abz UZ", "a9b0", "Abc z", "AEIOU aeiou", "0123456789",
			"The quick brown fox jumps over the lazy dog 42!"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		tests.append(TestCase(("".join(rng.choice("aeiuzZbBNy09 -!") for _ in range(rng.randint(1, 16))),)))
	return tests

EXERCISE = Exercise(
	name="letter_step",
	language="c",
	kind="program",
	assignment_name="step_${what}_${case}",
	expected_files=("step_${what}_${case}.c",),
	allowed_functions=("write",),
	themes=("letter_step",),
	params=(
		Param("what", ("vowels", "consonants", "digits", "backward_letters"), {
			"vowels": "each vowel replaced by the next vowel: a by e, e by i, i by o, o by u and u by a\n"
				"(y is not a vowel)",
			"consonants": "each consonant replaced by the next consonant in the alphabet: b by c,\n"
				"d by f, and z by b",
			"digits": "each digit replaced by the next digit: 0 by 1 and so on, and 9 by 0",
			"backward_letters": "each letter replaced by the letter before it in the alphabet: b by\n"
				"a, and a by z",
		}),
		Param("case", ("keep", "swap"), {
			"keep": "A character replaced keeps its case",
			"swap": "A character replaced also changes case: lowercase becomes uppercase\n"
				"and the reverse",
		}),
	),
	# Digits have no case: with swap, the same variant as with keep.
	forbidden=({"what": "digits", "case": "swap"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays it, followed by a\n"
		"newline, with\n"
		"$what.\n"
		"$case.\n"
		"Every other character is displayed as it is.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	examples=(
		TestCase(("Hello World",)),
		TestCase(("abz UZ 09",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
