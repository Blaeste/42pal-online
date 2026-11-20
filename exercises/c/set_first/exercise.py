"""set_first: an original program model in the style of "display the first z, or a z".

The program displays the first character of a string that is a vowel, a
digit, an uppercase letter or a punctuation sign; if there is none, or
without exactly one argument, it displays a fallback character instead.
The letter z, a real 42 subject, is never the character looked for.
"""

from pal42.model import Exercise, Param, TestCase

SETS = {
	"vowel": "aeiouAEIOU",
	"digit": "0123456789",
	"upper": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"punct": ".,;:!?",
}
FALLBACKS = {"question": "?", "dash": "-"}

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	fallback = FALLBACKS[params["fallback"]]
	if len(test.args) != 1:
		return fallback + "\n"
	for char in test.args[0]:
		if char in SETS[params["set"]]:
			return char + "\n"
	return fallback + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",))]
	for text in ["ab3c4", "abc", "hello World", "Hi, you!", "rhythm", "42 Is it?"]:
		tests.append(TestCase((text,)))
	for _ in range(6):
		tests.append(TestCase(("".join(rng.choice("bcxyZ17,!e ") for _ in range(rng.randint(1, 10))),)))
	return tests

EXERCISE = Exercise(
	name="set_first",
	language="c",
	kind="program",
	assignment_name="first_${set}_or_${fallback}",
	expected_files=("first_${set}_or_${fallback}.c",),
	allowed_functions=("write",),
	themes=("letter_or_fallback",),
	params=(
		Param("set", ("vowel", "digit", "upper", "punct"), {
			"vowel": "a vowel (a, e, i, o, u, in either case)",
			"digit": "a digit (0 to 9)",
			"upper": "an uppercase letter (A to Z)",
			"punct": "a punctuation sign: one of . , ; : ! and ?",
		}),
		Param("fallback", ("question", "dash"), {
			"question": "a question mark (?)",
			"dash": "a dash (-)",
		}),
	),
	subject=(
		"Write a program that takes one string and displays the first character of\n"
		"it that is\n"
		"$set,\n"
		"followed by a newline. If there is none, it displays\n"
		"$fallback\n"
		"followed by a newline.\n"
		"\n"
		"If the number of arguments is not 1, the program displays\n"
		"$fallback\n"
		"followed by a newline."
	),
	examples=(TestCase(("Hi, you! 42",)), TestCase(("abc",)), TestCase(())),
	oracle=oracle,
	generate_tests=generate_tests,
)
