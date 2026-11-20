"""replace_pick: an original program model in the style of "search and replace a character".

The program replaces some occurrences of a character in a string: the first,
the last, one out of two, or all but the first, with the exact case or in
either case. Replacing every occurrence with the exact case, a real 42
subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 3 or len(test.args[1]) != 1 or len(test.args[2]) != 1:
		return "\n"
	text, find, put = test.args
	if params["match"] == "exact":
		found = [i for i, char in enumerate(text) if char == find]
	else:
		found = [i for i, char in enumerate(text) if char.lower() == find.lower()]
	chosen = {
		"first": found[:1], "last": found[-1:],
		"every_other": found[::2], "all_but_first": found[1:],
	}[params["which"]]
	return "".join(put if i in chosen else char for i, char in enumerate(text)) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed cases, then random ones."""
	tests = [TestCase(args) for args in [
		(), ("abc",), ("abc", "ab", "x"), ("abc", "a", ""), ("a", "b", "c", "d"),
		("banana", "a", "o"), ("Abba", "a", "x"), ("Abba", "A", "-"), ("abc", "z", "x"),
		("", "a", "b"), ("aaaaa", "a", "a"), ("Hello World", "o", "0"), ("x x x", " ", "_"),
	]]
	for _ in range(8):
		text = "".join(rng.choice("aAbB c!") for _ in range(rng.randint(1, 14)))
		tests.append(TestCase((text, rng.choice("aAb "), rng.choice("x-Z"))))
	return tests

EXERCISE = Exercise(
	name="replace_pick",
	language="c",
	kind="program",
	assignment_name="replace_${which}_${match}",
	expected_files=("replace_${which}_${match}.c",),
	allowed_functions=("write",),
	themes=("char_replace",),
	params=(
		Param("which", ("first", "last", "every_other", "all_but_first"), {
			"first": "the first one",
			"last": "the last one",
			"every_other": "one out of two (the first, the third, the fifth and so on)",
			"all_but_first": "all of them but the first one",
		}),
		Param("match", ("exact", "any_case"), {
			"exact": "The character found must be exactly the one given",
			"any_case": "For a letter, both its lowercase and its uppercase are found (a\n"
				"finds a and A)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes three arguments: a string, a character to find\n"
		"and a character to put. Among the places where the character to find is in\n"
		"the string, it replaces\n"
		"$which\n"
		"by the character to put, then displays the string, followed by a newline.\n"
		"$match.\n"
		"\n"
		"If the number of arguments is not 3, or if the second or the third one is\n"
		"not a single character, the program displays only a newline."
	),
	examples=(
		TestCase(("banana", "a", "o")),
		TestCase(("Abba", "a", "x")),
		TestCase(("abc", "ab", "x")),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
