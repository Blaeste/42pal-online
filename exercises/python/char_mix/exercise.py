"""char_mix: an original Python model in the style of "compare the
characters of two strings".

The student writes a function that compares the characters of two strings:
those of the first only, those of one string only, or how many times each
common character can be paired. The characters common to both, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def once(chars):
	"""The characters of chars, each once, in the order of their first appearance."""
	return "".join(dict.fromkeys(chars))

def oracle(params, test):
	s1, s2 = values(test)
	rule = params["rule"]
	if rule == "only_first":
		return shown(once(char for char in s1 if char not in s2))
	if rule == "one_side":
		return shown(once(char for char in s1 if char not in s2) + once(char for char in s2 if char not in s1))
	return shown({char: min(s1.count(char), s2.count(char)) for char in once(s1) if char in s2})

def generate_tests(params, rng):
	pairs = [("hello", "world"), ("aab", "baaa"), ("", "abc"), ("abc", ""), ("same", "same"),
		("a b", "b c"), ("zzz", "z"), ("42 is", "the answer")]
	for _ in range(10):
		pairs.append(tuple("".join(rng.choice("abcde ") for _ in range(rng.randint(0, 10)))
			for _ in range(2)))
	return [case(s1, s2) for s1, s2 in pairs]

RULES = {
	"only_first": ("str", "a string of the characters of s1 that are not in s2, each once, in the\n"
		"order of their first appearance in s1"),
	"one_side": ("str", "a string of the characters that are in one of the two strings but not\n"
		"in the other, each once: first those of s1, in the order of their first\n"
		"appearance in s1, then those of s2, in the same way"),
	"common_count": ("dict[str, int]", "a dict that gives, for each character found in both\n"
		"strings, the smaller of its two numbers of appearances (in s1 and in\n"
		"s2); its keys come in the order of their first appearance in s1"),
}

EXERCISE = Exercise(
	name="char_mix",
	language="python",
	kind="function",
	assignment_name="mix_${rule}",
	expected_files=("mix_${rule}.py",),
	allowed_functions=(),
	themes=("shared_chars",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes two strings, s1 and s2, and returns\n"
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
	harness=harness("mix_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(s1: str, s2: str) -> {RULES[params['rule']][0]}:",
	examples=(case("hello", "world"), case("aab", "baaa")),
)
