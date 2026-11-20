"""mirror_group: an original program model in the style of "mirror the letters".

The program turns a group of characters around, like in a mirror: the
vowels (a and u swap), the consonants (b and z), the digits (0 and 9), or
each half of the alphabet (a and m, n and z); the characters of the group
may also change case. The whole alphabet in a mirror, a real 42 subject, is
not one of the groups.
"""

from pal42.model import Exercise, Param, TestCase

# Each group, in order: its first character swaps with its last, and so on.
GROUPS = {
	"vowels": ["aeiou"],
	"consonants": ["bcdfghjklmnpqrstvwxyz"],
	"digits": ["0123456789"],
	"halves": ["abcdefghijklm", "nopqrstuvwxyz"],
}

def mirrored(char, group):
	"""`char` turned around in its group, or None if it is in no part of the group."""
	lower = char.lower() if char.isascii() else char
	for part in GROUPS[group]:
		if lower in part:
			after = part[len(part) - 1 - part.index(lower)]
			return after.upper() if char.isupper() else after
	return None

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	result = ""
	for char in test.args[0]:
		after = mirrored(char, params["group"])
		if after is None:
			result += char
		else:
			result += after.swapcase() if params["case"] == "swap" else after
	return result + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",))]
	for text in ["Hello World", "abc xyz", "a1b9", "amnz", "in", "gt", "Ab c",
			"The quick brown fox jumps over the lazy dog 0123456789!"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		tests.append(TestCase(("".join(rng.choice("aeiouAbzMnY09 -!") for _ in range(rng.randint(1, 16))),)))
	return tests

EXERCISE = Exercise(
	name="mirror_group",
	language="c",
	kind="program",
	assignment_name="mirror_${group}_${case}",
	expected_files=("mirror_${group}_${case}.c",),
	allowed_functions=("write",),
	themes=("alphabet_mirror",),
	params=(
		Param("group", ("vowels", "consonants", "digits", "halves"), {
			"vowels": "the vowels: a by u, e by o, i stays i, o by e and u by a (y is not\n"
				"a vowel)",
			"consonants": "the consonants, in the order of the alphabet: b by z, c by y, d by x\n"
				"and so on, n staying n in the middle",
			"digits": "the digits: 0 by 9, 1 by 8 and so on, 9 by 0",
			"halves": "each half of the alphabet: from a to m, a by m, b by l and so on, g\n"
				"staying g; from n to z, n by z, o by y and so on, t staying t",
		}),
		Param("case", ("keep", "swap"), {
			"keep": "A character replaced keeps its case",
			"swap": "Each character of the group also changes case: lowercase becomes\n"
				"uppercase and the reverse",
		}),
	),
	# Digits have no case: with swap, the same variant as with keep.
	forbidden=({"group": "digits", "case": "swap"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays it, followed by a\n"
		"newline, with the characters of a group turned around like in a mirror,\n"
		"each one replaced by the one at the same place from the other end of the\n"
		"group. The group is\n"
		"$group.\n"
		"$case.\n"
		"Every other character is displayed as it is.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	examples=(
		TestCase(("Hello World 42",)),
		TestCase(("abc xyz",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
