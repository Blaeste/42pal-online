"""sentence_case: an original program model in the style of "convert a name to camelCase".

The program turns a sentence into one name, written in camelCase,
PascalCase, snake_case, kebab-case, CONSTANT_CASE or dot.case. Its input is
a sentence, words cut by any other character, not a name in snake_case like
the real 42 subject.
"""

import re

from pal42.model import Exercise, Param, TestCase

# The separator of each style, and how each word is written.
STYLES = {
	"camel": "", "pascal": "", "snake": "_", "kebab": "-", "constant": "_", "dot": ".",
}

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = [word.lower() for word in re.findall(r"[A-Za-z0-9]+", test.args[0])]
	style = params["style"]
	if style in ("camel", "pascal"):
		words = [word.capitalize() for word in words]
		if style == "camel" and words:
			words[0] = words[0].lower()
	elif style == "constant":
		words = [word.upper() for word in words]
	return STYLES[style].join(words) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed sentences, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase((" -!- ",))]
	for text in ["Hello, big WORLD 42!", "one", "  a  b  ", "it's 2 o'clock", "MiXeD cAsE"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		tests.append(TestCase(("".join(rng.choice("abCD12 ,.-!") for _ in range(rng.randint(1, 20))),)))
	return tests

EXERCISE = Exercise(
	name="sentence_case",
	language="c",
	kind="program",
	assignment_name="sentence_to_${style}",
	expected_files=("sentence_to_${style}.c",),
	allowed_functions=("write",),
	themes=("case_convert_back",),
	params=(
		Param("style", ("camel", "pascal", "snake", "kebab", "constant", "dot"), {
			"camel": "camelCase: the words joined, the first one in lowercase, each other\n"
				"one with an uppercase first letter (helloBigWorld)",
			"pascal": "PascalCase: the words joined, each one with an uppercase first letter\n"
				"(HelloBigWorld)",
			"snake": "snake_case: the words in lowercase, joined by _ (hello_big_world)",
			"kebab": "kebab-case: the words in lowercase, joined by - (hello-big-world)",
			"constant": "CONSTANT_CASE: the words in uppercase, joined by _ (HELLO_BIG_WORLD)",
			"dot": "dot.case: the words in lowercase, joined by . (hello.big.world)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string, a sentence, and displays its words\n"
		"as one name written in\n"
		"$style,\n"
		"followed by a newline.\n"
		"\n"
		"A word is a run of letters and digits; every other character separates\n"
		"words. The case of the letters given does not matter.\n"
		"\n"
		"If the number of arguments is not 1, or if there is no word, the program\n"
		"displays only a newline."
	),
	examples=(
		TestCase(("Hello, big WORLD 42!",)),
		TestCase(("it's 2 o'clock",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
