"""common_sorted: an original Python model in the style of "intersect sorted
lists".

The student writes a function that compares sorted lists: the values found
in at least m of them, the values common to all as many times as they all
have them, or the values found in one list only. The values found in every
list, the real subject, is not one of the rules.
"""

from collections import Counter

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def oracle(params, test):
	rule = params["rule"]
	if rule == "at_least":
		lists, m = values(test)
		seen = Counter(value for numbers in lists for value in set(numbers))
		return shown(sorted(value for value, count in seen.items() if count >= m))
	(lists,) = values(test)
	if rule == "only_one":
		seen = Counter(value for numbers in lists for value in set(numbers))
		return shown(sorted(value for value, count in seen.items() if count == 1))
	if not lists:
		return shown([])
	common = Counter(lists[0])
	for numbers in lists[1:]:
		common &= Counter(numbers)
	return shown(sorted(common.elements()))

def random_lists(rng):
	return [sorted(rng.randint(0, 8) for _ in range(rng.randint(0, 6))) for _ in range(rng.randint(1, 4))]

def generate_tests(params, rng):
	fixed = [[[1, 2, 2, 3], [2, 2, 3, 4], [2, 3, 3, 5]], [[1, 1, 2], [1, 1, 1, 2, 2]], [], [[]], [[4, 4]],
		[[1, 2], [3, 4]], [[-2, 0, 0], [-2, -2, 0]]]
	lists = fixed + [random_lists(rng) for _ in range(10)]
	if params["rule"] == "at_least":
		return [case(numbers, m) for numbers, m in zip(lists, [2, 1, 1, 1, 1, 2, 2] + [rng.randint(1, 3)
			for _ in range(10)])]
	return [case(numbers) for numbers in lists]

RULES = {
	"at_least": ("lists: list[list[int]], m: int", "and an int m from 1, and returns the values\n"
		"found in at least m of the lists"),
	"with_counts": ("lists: list[list[int]]", "and returns the values found in every list, each\n"
		"one as many times as it is in the list that has it the fewest times (no\n"
		"list gives an empty list)"),
	"only_one": ("lists: list[list[int]]", "and returns the values found in one of the lists\n"
		"only, however many times they are in it"),
}

EXERCISE = Exercise(
	name="common_sorted",
	language="python",
	kind="function",
	assignment_name="common_${rule}",
	expected_files=("common_${rule}.py",),
	allowed_functions=(),
	themes=("sorted_intersection",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a list of lists of ints, each sorted from the\n"
		"smallest to the largest value,\n"
		"$rule.\n"
		"\n"
		"The result is a new list sorted from the smallest to the largest value,\n"
		"where each value appears once unless said otherwise. The given lists must\n"
		"not be changed.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("common_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> list[int]:",
	examples=lambda params: {
		"at_least": (case([[1, 2, 2, 3], [2, 2, 3, 4], [2, 3, 3, 5]], 2),),
		"with_counts": (case([[1, 1, 2], [1, 1, 1, 2, 2]]), case([[1, 2], [3, 4]])),
		"only_one": (case([[1, 2, 2, 3], [2, 2, 3, 4], [2, 3, 3, 5]]),),
	}[params["rule"]],
)
