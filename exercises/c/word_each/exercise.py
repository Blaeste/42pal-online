"""word_each: an original program model in the style of "display a word of a
string".

The program takes any number of strings and displays one word of each: the
shortest, the longest or the second one, a line for each string or all on
one line. The first word of one string, the real 42 subject, is not one of
the variants.
"""

import re

from pal42.model import Exercise, Param, TestCase

def picked(text, which):
	"""The word of text the variant displays, or None."""
	words = re.findall(r"[^ \t]+", text)
	if which == "second":
		return words[1] if len(words) > 1 else None
	if not words:
		return None
	size = (min if which == "shortest" else max)(map(len, words))
	return next(word for word in words if len(word) == size)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if not test.args:
		return "\n"
	words = [picked(text, params["which"]) for text in test.args]
	if params["join"] == "lines":
		return "".join((word or "") + "\n" for word in words)
	return " ".join(word for word in words if word is not None) + "\n"

def generate_tests(params, rng):
	tests = [TestCase(()), TestCase(("one three two", "  a bb ", "")), TestCase(("x yy zzz q", "solo")),
		TestCase(("\tsame size\t",)), TestCase(("",)), TestCase(("a", "b c", "d e f"))]
	for _ in range(8):
		tests.append(TestCase(tuple(" ".join("".join(rng.choice("abxy") for _ in range(rng.randint(1, 5)))
			for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(1, 4)))))
	return tests

EXERCISE = Exercise(
	name="word_each",
	language="c",
	kind="program",
	assignment_name="${which}_word_${join}",
	expected_files=("${which}_word_${join}.c",),
	allowed_functions=("write",),
	themes=("find_word",),
	params=(
		Param("which", ("shortest", "longest", "second"), {
			"shortest": "its shortest word (the first one of that length if several are)",
			"longest": "its longest word (the first one of that length if several are)",
			"second": "its second word",
		}),
		Param("join", ("lines", "spaces"), {
			"lines": "each followed by a newline: one line for each string, an empty line for\n"
				"a string that has no such word",
			"spaces": "all on one line, separated by one space, then a newline; a string that\n"
				"has no such word gives nothing",
		}),
	),
	subject=(
		"Write a program that takes any number of strings and displays, for each\n"
		"string in order,\n"
		"$which,\n"
		"$join.\n"
		"\n"
		"A word is a group of characters that are not spaces nor tabs, as long as it\n"
		"can be.\n"
		"\n"
		"If there is no argument, the program displays a newline."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	examples=(TestCase(("one three two", "  a bb ", "")), TestCase(("x yy zzz q", "solo")), TestCase(())),
)
