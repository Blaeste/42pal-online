"""char_filter: an original model on the theme "character sets" (char_sets).

The program gets two strings and prints a set of their characters: the ones
found in both, or the ones of only one string. The variants change which
set, in what order and with what separator. The combination that gives
back the real exam subject of this theme is forbidden.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 2:
		return "\n"
	s1, s2 = test.args
	chars = []
	# Reading s1, then s2, gives the order of first appearance.
	for char in s1 + s2:
		if belongs(params["mode"], char, s1, s2) and char not in chars:
			chars.append(char)
	if params["order"] == "ascii":
		# Python sorts characters by code, which is the ASCII value for
		# ASCII characters (the only ones the tests use).
		chars.sort()
	# join puts the separator only between the characters, never at the ends.
	separator = " " if params["separator"] == "space" else ""
	return separator.join(chars) + "\n"

def belongs(mode, char, s1, s2):
	"""True when `char` is in the set of characters that `mode` asks for."""
	if mode == "common":
		return char in s1 and char in s2
	if mode == "only_first":
		return char in s1 and char not in s2
	return char in s2 and char not in s1

# A small alphabet, so that two random strings often share characters;
# printable ASCII only, with a space, digits and symbols.
ALPHABET = "abcdefghij 0123!?"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random ones.

	The same rng (same seed) gives the same tests. They do not depend on
	params: every variant is graded on the same arguments.
	"""
	tests = [
		# Wrong number of arguments.
		TestCase(()),
		TestCase(("only one",)),
		TestCase(("one", "two", "three")),
		# Empty strings, the same string twice, repeated characters, spaces.
		TestCase(("", "")),
		TestCase(("abc", "")),
		TestCase(("", "abc")),
		TestCase(("same", "same")),
		TestCase(("aaaa", "a")),
		TestCase(("hello world", "lower case")),
	]
	for _ in range(10):
		tests.append(TestCase((random_string(rng), random_string(rng))))
	return tests

def random_string(rng):
	"""Return a string of 0 to 15 characters of ALPHABET, drawn with rng."""
	length = rng.randint(0, 15)
	return "".join(rng.choice(ALPHABET) for _ in range(length))

EXERCISE = Exercise(
	name="char_filter",
	language="c",
	kind="program",
	assignment_name="${mode}_chars",
	expected_files=("${mode}_chars.c",),
	allowed_functions=("write",),
	themes=("common_chars",),
	params=(
		Param("mode", ("common", "only_first", "only_second"), {
			"common": "that appears in both s1 and s2",
			"only_first": "of s1 that never appears in s2",
			"only_second": "of s2 that never appears in s1",
		}),
		Param("order", ("appearance", "ascii"), {
			"appearance": "in the order they first appear when reading s1, then s2",
			"ascii": "sorted by increasing ASCII value",
		}),
		Param("separator", ("none", "space"), {
			"none": "written next to each other",
			"space": "separated by one space, with no space at the ends",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters
	# whatever the texts put in them.
	subject=(
		"This program receives two strings as arguments, s1 and s2.\n"
		"\n"
		"It prints every character $mode,\n"
		"$order.\n"
		"Each character is printed only once, even if it appears several times.\n"
		"\n"
		"The characters are $separator,\n"
		"and a newline ends the line.\n"
		"\n"
		"With any other number of arguments, it prints only a newline."
	),
	examples=(
		TestCase(("programming", "gaming")),
		TestCase(("mulhouse", "house42")),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
	# The characters found in both strings, in the order of s1, with nothing
	# between them: that is the real exam subject of this theme.
	forbidden=({"mode": "common", "order": "appearance", "separator": "none"},),
)
