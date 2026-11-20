"""letter_bag: an original Python model in the style of "compare strings by
the letters they hold".

The student writes a function that counts letters: those missing to make a
string hold all the letters of another, groups of words made of the same
letters, or whether a word can be written with the letters of a text.
Saying whether two strings hold the same letters, the real subject, is not
one of the rules.
"""

from collections import Counter

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def letters(text):
	"""The letters a to z of text, case ignored, counted."""
	return Counter(char for char in text.lower() if "a" <= char <= "z")

def oracle(params, test):
	rule = params["rule"]
	if rule == "missing":
		have, want = values(test)
		return shown("".join(sorted((letters(want) - letters(have)).elements())))
	if rule == "can_write":
		word, text = values(test)
		return shown(not letters(word) - letters(text))
	(words,) = values(test)
	groups = {}
	for word in words:
		groups.setdefault(tuple(sorted(letters(word).elements())), []).append(word)
	return shown(list(groups.values()))

def random_word(rng):
	return "".join(rng.choice("aeltsnoT") for _ in range(rng.randint(1, 5)))

def generate_tests(params, rng):
	rule = params["rule"]
	if rule == "groups":
		lists = [[], ["Listen", "pots", "silent", "stop", "x"], ["a"], ["ab", "BA", "a b", "ba!"],
			["", "", "x"]]
		lists += [[random_word(rng) for _ in range(rng.randint(2, 7))] for _ in range(10)]
		return [case(words) for words in lists]
	pairs = [("Hello", "hello world"), ("abc", "CAB!"), ("Tea", "a tree"), ("teet", "a tree"),
		("", "abc"), ("abc", ""), ("A-a", "aa"), ("zz", "z z")]
	pairs += [(random_word(rng), " ".join(random_word(rng) for _ in range(2))) for _ in range(10)]
	return [case(a, b) for a, b in pairs]

RULES = {
	"missing": ("have: str, want: str", "str", "takes two strings, have and want, and returns the\n"
		"letters to add to have so that it holds each letter of want at least as\n"
		"many times as want does: a string of these letters in lower case, in\n"
		"alphabetical order, each letter as many times as it is missing"),
	"groups": ("words: list[str]", "list[list[str]]", "takes a list of words and returns them in\n"
		"groups: a list of lists, one for each set of words that hold the same\n"
		"letters the same number of times. The groups come in the order of their\n"
		"first word in the given list, and the words of a group in that order\n"
		"too"),
	"can_write": ("word: str, text: str", "bool", "takes a word and a text, and returns True if\n"
		"the word can be written with the letters of the text, each letter of the\n"
		"text used once at most, and False otherwise"),
}

EXERCISE = Exercise(
	name="letter_bag",
	language="python",
	kind="function",
	assignment_name="bag_${rule}",
	expected_files=("bag_${rule}.py",),
	allowed_functions=(),
	themes=("same_letters",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that\n"
		"$rule.\n"
		"\n"
		"Only the letters a to z count, in either case (A and a are the same\n"
		"letter); every other character is ignored.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("bag_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"missing": (case("Hello", "hello world"), case("abc", "CAB!")),
		"groups": (case(["Listen", "pots", "silent", "stop", "x"]),),
		"can_write": (case("Tea", "a tree"), case("teet", "a tree")),
	}[params["rule"]],
)
