"""key_sort: an original Python model in the style of "sort strings on
several keys without sorted()".

The student writes a function that sorts a list of strings on two keys of
the variant (consonants then lower case, last character then length, or
digits then length), keeping the order of the given list for ties, without
sorted() nor list.sort(). The keys of the real subject (length, then
letters without case, then vowels) are not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

VOWELS = "aeiouAEIOU"

def consonants(word):
	return sum(1 for char in word if char.isascii() and char.isalpha() and char not in VOWELS)

KEYS = {
	"consonants": lambda word: (consonants(word), word.lower()),
	"last_char": lambda word: (word[-1:], -len(word)),
	"digits": lambda word: (-sum(char.isdigit() for char in word), len(word)),
}

def oracle(params, test):
	(words,) = values(test)
	# sorted() is stable: equal keys keep the order of the given list.
	return shown(sorted(words, key=KEYS[params["rule"]]))

def generate_tests(params, rng):
	lists = [
		[], ["one"], ["street", "Aia", "bob", "eau", "Bob", "tree"], ["ab", "", "zzb", "a", "Ba"],
		["a1", "b22", "c", "1d2", "x"], ["same", "same", "Same"], ["9", "z", "Z", "a9", ""],
	]
	for _ in range(10):
		lists.append(["".join(rng.choice("abeiouxyzAB12") for _ in range(rng.randint(0, 6)))
			for _ in range(rng.randint(2, 8))])
	return [case(words) for words in lists]

EXERCISE = Exercise(
	name="key_sort",
	language="python",
	kind="function",
	assignment_name="sort_by_${rule}",
	expected_files=("sort_by_${rule}.py",),
	allowed_functions=(),
	forbidden_calls=("sorted", "sort"),
	themes=("multi_key_sort",),
	params=(
		Param("rule", ("consonants", "last_char", "digits"), {
			"consonants": "by their number of consonants, fewest first; then, among strings with\n"
				"as many, in the alphabetical order of the strings written in lower case,\n"
				"comparing the characters by their ASCII code. The consonants are the\n"
				"letters other than a, e, i, o and u, in either case",
			"last_char": "by their last character, in ASCII order (an empty string comes first),\n"
				"then from the longest to the shortest",
			"digits": "by their number of digits, most first, then from the shortest to the\n"
				"longest",
		}),
	),
	subject=(
		"Write a function that takes a list of strings and returns a new list with\n"
		"the same strings, sorted\n"
		"$rule.\n"
		"\n"
		"Strings that these rules cannot tell apart keep their order of the given\n"
		"list. The given list must not be changed. You may not use sorted() nor the\n"
		"sort() method of lists.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(words: list[str]) -> list[str]:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("sort_by_${rule}"),
	call=call,
	examples=(case(["street", "Aia", "bob", "eau", "Bob", "tree"]), case(["a1", "b22", "c", "1d2", "x"])),
)
