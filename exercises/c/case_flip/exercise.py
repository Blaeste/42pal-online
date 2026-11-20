"""case_flip: an original program model in the style of "change the case of letters".

The program changes the case of some letters of a string: it swaps their
case, or puts them in uppercase or in lowercase. The letters changed are the
vowels, the consonants, one letter out of two, or the first letter of each
word. Swapping the case of every letter, a real 42 subject, is not one of
the variants.
"""

from pal42.model import Exercise, Param, TestCase

VOWELS = "aeiouAEIOU"

def chosen(letters, text):
	"""The indexes of the letters of `text` that the variant changes."""
	places = []
	count = 0
	for index, char in enumerate(text):
		if not char.isascii() or not char.isalpha():
			continue
		if letters == "vowels" and char in VOWELS:
			places.append(index)
		elif letters == "consonants" and char not in VOWELS:
			places.append(index)
		elif letters == "every_other" and count % 2 == 0:
			places.append(index)
		elif letters == "word_starts" and (index == 0 or text[index - 1] in " \t"):
			places.append(index)
		count += 1
	return places

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	text = list(test.args[0])
	for index in chosen(params["letters"], test.args[0]):
		if params["action"] == "swap":
			text[index] = text[index].swapcase()
		elif params["action"] == "upper":
			text[index] = text[index].upper()
		else:
			text[index] = text[index].lower()
	return "".join(text) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",))]
	for text in ["Hello World", "YES you", "a-b c!d", "ABCD", "  hello  wORLD\tx 42abc",
			"AeIoU yY", "42 is The Answer!"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		tests.append(TestCase(("".join(rng.choice("abEiOuxYZ  -!7\t")
			for _ in range(rng.randint(1, 20))),)))
	return tests

EXERCISE = Exercise(
	name="case_flip",
	language="c",
	kind="program",
	assignment_name="${action}_${letters}",
	expected_files=("${action}_${letters}.c",),
	allowed_functions=("write",),
	themes=("case_swap",),
	params=(
		Param("action", ("swap", "upper", "lower"), {
			"swap": "with its case swapped (lowercase becomes uppercase and the reverse)",
			"upper": "in uppercase",
			"lower": "in lowercase",
		}),
		Param("letters", ("vowels", "consonants", "every_other", "word_starts"), {
			"vowels": "every vowel (a, e, i, o, u, in either case; y is not one)",
			"consonants": "every consonant (every letter that is not a, e, i, o or u)",
			"every_other": "one letter out of two: the first, the third, the fifth letter of\n"
				"the string and so on (other characters are not counted)",
			"word_starts": "the first character of each word, if it is a letter (words are cut\n"
				"by spaces and tabs)",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays it, followed by a\n"
		"newline, with\n"
		"$letters,\n"
		"$action.\n"
		"Every other character is displayed as it is.\n"
		"\n"
		"If the number of arguments is not 1, the program displays only a newline."
	),
	examples=(
		TestCase(("Hello World",)),
		TestCase(("42 is The Answer!",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
