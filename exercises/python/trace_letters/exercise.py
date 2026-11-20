"""trace_letters: an original Python model in the style of "find the letters
of a word, in order, in another string".

The student writes a function that looks for the characters of small, in
order, in big: where they are, how many times they can be found one after
the other, or whether they are there with case ignored. The same test with
case, a real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def positions(small, big):
	found = []
	for index, char in enumerate(big):
		if len(found) < len(small) and char == small[len(found)]:
			found.append(index)
	return found if len(found) == len(small) else None

def oracle(params, test):
	small, big = values(test)
	rule = params["rule"]
	if rule == "positions":
		return shown(positions(small, big))
	if rule == "nocase":
		return shown(positions(small.lower(), big.lower()) is not None)
	count, wanted = 0, 0
	for char in big if small else "":
		if char == small[wanted]:
			wanted += 1
			if wanted == len(small):
				count, wanted = count + 1, 0
	return shown(count)

def generate_tests(params, rng):
	pairs = [("abc", "xaxbxcx"), ("abc", "cba"), ("", "abc"), ("ab", "aabb ab"), ("ab", "ba"),
		("AbC", "xaYBzc"), ("ab", "BA"), ("a", ""), ("aa", "aaaaa"), ("Hi", "oh hi Hi HI")]
	for _ in range(10):
		small = "".join(rng.choice("abAB") for _ in range(rng.randint(1, 3)))
		big = "".join(rng.choice("abAB x") for _ in range(rng.randint(0, 14)))
		pairs.append((small, big))
	return [case(small, big) for small, big in pairs]

RULES = {
	"positions": ("list[int] | None", "the list of the indexes in big where its characters\n"
		"are found, each one as early as possible after the one before; None if\n"
		"they cannot all be found that way, and an empty list for an empty small"),
	"count": ("int", "how many times its characters can be found that way, going through\n"
		"big once from its start: after each time all of them are found, the\n"
		"search starts again from the first character of small (0 for an empty\n"
		"small)"),
	"nocase": ("bool", "True if they can be found that way when the case of the letters is\n"
		"ignored (a and A are then the same), and False otherwise"),
}

EXERCISE = Exercise(
	name="trace_letters",
	language="python",
	kind="function",
	assignment_name="trace_${rule}",
	expected_files=("trace_${rule}.py",),
	allowed_functions=(),
	themes=("subsequence_check",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes two strings, small and big. The characters of\n"
		"small are found in big when they appear in big in the same order, not\n"
		"necessarily next to each other. The function returns\n"
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
	harness=harness("trace_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(small: str, big: str) -> {RULES[params['rule']][0]}:",
	examples=(case("abc", "xaxbxcx"), case("ab", "aabb ab"), case("AbC", "xaYBzc")),
)
