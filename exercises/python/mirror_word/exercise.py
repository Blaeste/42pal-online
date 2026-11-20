"""mirror_word: an original Python model in the style of "read a string the
same way from both ends".

The student writes a function about palindromes: the digits of a string,
the longest word that is one, or a string that becomes one when a letter is
taken out. The letters of the whole string read both ways, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def is_mirror(chars):
	return chars == chars[::-1]

def oracle(params, test):
	(text,) = values(test)
	rule = params["rule"]
	if rule == "digits":
		return shown(is_mirror([char for char in text if char.isdigit()]))
	if rule == "longest_word":
		best = ""
		for word in text.split(" "):
			if word and is_mirror(word.lower()) and len(word) > len(best):
				best = word
		return shown(best)
	letters = [char.lower() for char in text if char.isalpha()]
	return shown(any(is_mirror(letters[:i] + letters[i + 1:]) for i in range(len(letters)))
		or is_mirror(letters))

def generate_tests(params, rng):
	texts = ["", "a", "1a2b-3", "12x21", "no digit", "Anna saw a Kayak at noon", "abc de",
		"Ra-ce car", "abca", "abcda", "Level up 2002", "ab  ba", "Xx yY"]
	for _ in range(10):
		texts.append("".join(rng.choice("abAB12 -") for _ in range(rng.randint(1, 12))))
	return [case(text) for text in texts]

RULES = {
	"digits": ("bool", "True if the digits of the string, read from the end, are the same\n"
		"as read from the start, and False otherwise (a string without digits\n"
		"gives True); the other characters are ignored"),
	"longest_word": ("str", "the longest word of the string that reads the same from both ends,\n"
		"case ignored; the first one if several have that length, and an empty\n"
		"string if there is none. The words are separated by spaces, and a word\n"
		"of one letter reads the same from both ends"),
	"near": ("bool", "True if the letters of the string, case ignored, read the same from\n"
		"both ends, or would after taking out one of them; False otherwise. The\n"
		"other characters are ignored"),
}

EXERCISE = Exercise(
	name="mirror_word",
	language="python",
	kind="function",
	assignment_name="mirror_${rule}",
	expected_files=("mirror_${rule}.py",),
	allowed_functions=(),
	themes=("palindrome_check",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a string and returns\n"
		"$rule.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("mirror_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(text: str) -> {RULES[params['rule']][0]}:",
	examples=lambda params: {
		"digits": (case("12x21"), case("1a2b-3")),
		"longest_word": (case("Anna saw a Kayak at noon"), case("abc de")),
		"near": (case("Ra-ce car"), case("abca"), case("abcda")),
	}[params["rule"]],
)
