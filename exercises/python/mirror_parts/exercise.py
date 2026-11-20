"""mirror_parts: an original Python model in the style of "cut a string into
palindromes with dynamic programming".

The student writes a function that cuts a string into parts that read the
same from both ends: how many ways there are, a cut with the fewest parts,
or the fewest parts when no part may be a single character. The fewest cuts,
the real subject, is not one of the rules.
"""

from functools import lru_cache

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def is_mirror(text):
	return text == text[::-1]

def oracle(params, test):
	(text,) = values(test)
	rule = params["rule"]

	@lru_cache(maxsize=None)
	def ways(start):
		if start == len(text):
			return 1
		return sum(ways(end) for end in range(start + 1, len(text) + 1) if is_mirror(text[start:end]))

	@lru_cache(maxsize=None)
	def fewest(start, shortest):
		"""The best cut of text[start:] with parts of at least `shortest` characters, or None."""
		if start == len(text):
			return ()
		best = None
		# From the longest first part: on a tie, the longest first part wins.
		for end in range(len(text), start + shortest - 1, -1):
			if is_mirror(text[start:end]):
				rest = fewest(end, shortest)
				if rest is not None and (best is None or len(rest) + 1 < len(best)):
					best = (text[start:end],) + rest
		return best

	if rule == "ways":
		return shown(ways(0))
	if rule == "fewest":
		return shown(list(fewest(0, 1)))
	best = fewest(0, 2)
	return shown(-1 if best is None else len(best))

def generate_tests(params, rng):
	texts = ["", "a", "aab", "aaa", "abacdc", "abab", "aabb", "abba", "racecar", "abc", "aabbaa", "noonabba"]
	for _ in range(10):
		texts.append("".join(rng.choice("ab") for _ in range(rng.randint(1, 12))))
	return [case(text) for text in texts]

RULES = {
	"ways": ("int", "the number of ways to cut the string into parts that all read the same\n"
		"from both ends (the string itself, not cut, is one way if it reads the\n"
		"same from both ends). An empty string gives 1"),
	"fewest": ("list[str]", "the list of the parts of a cut into parts that all read the same\n"
		"from both ends, with the fewest parts. When several cuts have that many\n"
		"parts, the one whose first part is the longest, then whose second part\n"
		"is the longest, and so on. An empty string gives an empty list"),
	"no_single": ("int", "the fewest number of parts of a cut into parts that all read the same\n"
		"from both ends and all have at least 2 characters; -1 if there is no\n"
		"such cut. An empty string gives 0"),
}

EXERCISE = Exercise(
	name="mirror_parts",
	language="python",
	kind="function",
	assignment_name="parts_${rule}",
	expected_files=("parts_${rule}.py",),
	allowed_functions=(),
	themes=("palindrome_cuts",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a string and returns\n"
		"$rule.\n"
		"\n"
		"The parts of a cut are characters next to each other; put back in order,\n"
		"they give the string. A string reads the same from both ends when it is\n"
		"the same reversed (every character counts, case too).\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("parts_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(text: str) -> {RULES[params['rule']][0]}:",
	examples=lambda params: {
		"ways": (case("aab"), case("aaa")),
		"fewest": (case("abacdc"), case("abab")),
		"no_single": (case("aabb"), case("aab")),
	}[params["rule"]],
)
