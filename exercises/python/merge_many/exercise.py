"""merge_many: an original Python model in the style of "merge many sorted
lists".

The student writes a function that walks many sorted lists at the same
time: lists sorted from the largest, the k smallest values only, or the
list each value of the merge comes from, without sorted() nor list.sort().
Many lists sorted from the smallest merged into one, the real subject, is
not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def origins(lists):
	places = [0] * len(lists)
	found = []
	while True:
		heads = [(lists[i][places[i]], i) for i in range(len(lists)) if places[i] < len(lists[i])]
		if not heads:
			return found
		_, index = min(heads)
		found.append(index)
		places[index] += 1

def oracle(params, test):
	rule = params["rule"]
	if rule == "first_k":
		lists, k = values(test)
		return shown(sorted(value for numbers in lists for value in numbers)[:k])
	(lists,) = values(test)
	if rule == "descending":
		return shown(sorted((value for numbers in lists for value in numbers), reverse=True))
	return shown(origins(lists))

def generate_tests(params, rng):
	rule = params["rule"]
	# Sorted from the smallest; turned around below for the descending rule.
	fixed = [[[1, 4], [2, 3], [1]], [[1, 9], [5, 5], []], [], [[], []], [[1], []], [[2, 2], [2], [1, 2, 3]]]
	lists = fixed + [[sorted(rng.randint(-5, 9) for _ in range(rng.randint(0, 5)))
		for _ in range(rng.randint(1, 4))] for _ in range(10)]
	if rule == "descending":
		lists = [[numbers[::-1] for numbers in group] for group in lists]
	if rule == "first_k":
		return [case(group, k) for group, k in zip(lists, [3, 2, 1, 4, 5, 0] + [rng.randint(0, 8)
			for _ in range(10)])]
	return [case(group) for group in lists]

RULES = {
	"descending": ("lists: list[list[int]]", "list[int]", "Each list is sorted from the largest\n"
		"to the smallest value; the function returns a new list of all their\n"
		"values, sorted the same way"),
	"first_k": ("lists: list[list[int]], k: int", "list[int]", "Each list is sorted from the\n"
		"smallest to the largest value, and k is from 0; the function returns the\n"
		"k smallest values of all the lists, a value found several times counting\n"
		"each time, sorted from the smallest; all the values if there are fewer\n"
		"than k"),
	"origins": ("lists: list[list[int]]", "list[int]", "Each list is sorted from the smallest\n"
		"to the largest value. Merging them takes, at each step, the smallest of\n"
		"the first values left in the lists (from the list of smallest index when\n"
		"several are equal). The function returns, for each step, the index of\n"
		"the list the value is taken from"),
}

EXERCISE = Exercise(
	name="merge_many",
	language="python",
	kind="function",
	assignment_name="many_${rule}",
	expected_files=("many_${rule}.py",),
	allowed_functions=(),
	forbidden_calls=("sorted", "sort"),
	themes=("k_way_merge",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a list of lists of ints, that may be empty.\n"
		"$rule.\n"
		"\n"
		"The given lists must not be changed. You may not use sorted() nor the\n"
		"sort() method of lists: go through the lists side by side.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("many_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"descending": (case([[9, 1], [5, 5], []]),),
		"first_k": (case([[1, 4], [2, 3], [1]], 3), case([[1], []], 5)),
		"origins": (case([[1, 4], [2, 3], [1]]),),
	}[params["rule"]],
)
