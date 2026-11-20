"""char_balance: an original Python model in the style of "count the
characters of two strings".

The student writes a function that compares how many times each character
appears in two strings: how many characters to change for one to be a
reordering of the other, the first character in excess, or where a
reordering of a string starts inside another. Saying whether two strings
are reorderings of each other, the real subject, is not one of the rules.
"""

from collections import Counter

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def oracle(params, test):
	first, second = values(test)
	rule = params["rule"]
	if rule == "changes":
		if len(first) != len(second):
			return shown(-1)
		return shown(sum((Counter(first) - Counter(second)).values()))
	if rule == "first_extra":
		extra = Counter(first) - Counter(second)
		return shown(next((char for char in first if extra[char]), ""))
	size, wanted = len(first), Counter(first)
	return shown(next((start for start in range(len(second) - size + 1)
		if Counter(second[start:start + size]) == wanted), -1))

def generate_tests(params, rng):
	pairs = [("aabc", "abcd"), ("ab", "abc"), ("banana", "abn"), ("ab", "ba"), ("ab", "xxbay"),
		("aB", "abba"), ("", ""), ("", "abc"), ("a a", "aa "), ("xyz", "zyx"), ("abc", "ab")]
	for _ in range(10):
		pairs.append(("".join(rng.choice("abcA ") for _ in range(rng.randint(0, 4))),
			"".join(rng.choice("abcA ") for _ in range(rng.randint(0, 10)))))
	return [case(a, b) for a, b in pairs]

RULES = {
	"changes": ("s1: str, s2: str", "int", "takes two strings, s1 and s2, and returns the smallest\n"
		"number of characters of s1 to replace by other characters so that s1\n"
		"holds the same characters as s2, as many times each, in any order; or\n"
		"-1 if the two strings do not have the same length"),
	"first_extra": ("s1: str, s2: str", "str", "takes two strings, s1 and s2, and returns the first\n"
		"character of s1 that appears more times in s1 than in s2; or an empty\n"
		"string if there is none"),
	"window": ("small: str, big: str", "int", "takes two strings, small and big. A part of big\n"
		"is as many characters as small has, next to each other in big. The\n"
		"function returns the index of the first part of big that holds the same\n"
		"characters as small, as many times each, in any order; -1 if there is\n"
		"none, and 0 for an empty small"),
}

EXERCISE = Exercise(
	name="char_balance",
	language="python",
	kind="function",
	assignment_name="balance_${rule}",
	expected_files=("balance_${rule}.py",),
	allowed_functions=(),
	themes=("char_multiset",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that\n"
		"$rule.\n"
		"\n"
		"Every character counts, spaces too, and the case matters (a and A are two\n"
		"characters).\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("balance_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"changes": (case("aabc", "abcd"), case("ab", "abc")),
		"first_extra": (case("banana", "abn"), case("ab", "ba")),
		"window": (case("ab", "xxbay"), case("aB", "abba")),
	}[params["rule"]],
)
