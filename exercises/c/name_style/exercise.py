"""name_style: an original program model on the theme "writing styles of names".

The program takes a name written in one style (snake_case, kebab-case,
camelCase, PascalCase or CONSTANT_CASE) and displays it in another one.
camelCase to snake_case and back are real 42 subjects: both are left out,
like the pairs of a style with itself.
"""

from pal42.model import Exercise, Param, TestCase

STYLE_NAMES = ("snake", "kebab", "camel", "pascal", "constant")

# How the subject describes each style, with the same example name.
STYLE_TEXTS = {
	"snake": "snake_case (words in lowercase, joined by _: big_red_box)",
	"kebab": "kebab-case (words in lowercase, joined by -: big-red-box)",
	"camel": "camelCase (words joined, the first one in lowercase, each other one\n"
		"with an uppercase first letter: bigRedBox)",
	"pascal": "PascalCase (words joined, each one with an uppercase first letter:\n"
		"BigRedBox)",
	"constant": "CONSTANT_CASE (words in uppercase, joined by _: BIG_RED_BOX)",
}

def split_name(style, name):
	"""The words of `name`, written in `style`, in lowercase."""
	if not name:
		return []
	if style in ("snake", "constant"):
		return name.lower().split("_")
	if style == "kebab":
		return name.split("-")
	# camelCase and PascalCase: each uppercase letter starts a new word.
	words = []
	for char in name:
		if char.isupper() or not words:
			words.append(char.lower())
		else:
			words[-1] += char
	return words

def join_words(style, words):
	"""`words` (in lowercase) written as one name in `style`."""
	if style == "snake":
		return "_".join(words)
	if style == "kebab":
		return "-".join(words)
	if style == "constant":
		return "_".join(words).upper()
	capitalized = [word.capitalize() for word in words]
	if style == "camel" and words:
		capitalized[0] = words[0]
	return "".join(capitalized)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	words = split_name(params["source"], test.args[0])
	return join_words(params["target"], words) + "\n"

def written_in(style, *word_lists):
	"""One test per list of words, written as a name in `style`."""
	return [TestCase((join_words(style, words),)) for words in word_lists]

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed edge cases, then random names."""
	tests = [TestCase(()), TestCase(("big", "box")), TestCase(("",))]
	tests += written_in(params["source"],
		["hello"], ["a", "b", "c"], ["x"], ["the", "quick", "brown", "fox", "jumps"])
	for _ in range(10):
		words = [
			"".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(1, 7)))
			for _ in range(rng.randint(1, 5))
		]
		tests += written_in(params["source"], words)
	return tests

def examples(params):
	"""The examples of the subject, written in the source style of the variant."""
	return (*written_in(params["source"], ["big", "red", "box"], ["hello"]), TestCase(()))

EXERCISE = Exercise(
	name="name_style",
	language="c",
	kind="program",
	assignment_name="${source}_to_${target}",
	expected_files=("${source}_to_${target}.c",),
	allowed_functions=("write",),
	themes=("case_convert",),
	params=(
		Param("source", STYLE_NAMES, STYLE_TEXTS),
		Param("target", STYLE_NAMES, STYLE_TEXTS),
	),
	# A style into itself does nothing; camel_to_snake and snake_to_camel
	# are real subjects.
	forbidden=(
		*({"source": style, "target": style} for style in STYLE_NAMES),
		{"source": "camel", "target": "snake"},
		{"source": "snake", "target": "camel"},
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string, a name written in\n"
		"$source,\n"
		"and displays the same name written in\n"
		"$target,\n"
		"followed by a newline.\n"
		"\n"
		"The name is always written right in the first style, with words made of\n"
		"letters only (a to z, in uppercase where the style asks for it). An empty\n"
		"string gives only a newline.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	examples=examples,
	oracle=oracle,
	generate_tests=generate_tests,
)
