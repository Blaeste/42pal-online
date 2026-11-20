"""merge_twist: an original Python model in the style of "merge two sorted
lists in one pass".

The student writes a function that walks two sorted lists at the same
time: lists sorted from the largest, each value kept once, or the path of
the merge (which list each value comes from), without sorted() nor
list.sort(). Two lists sorted from the smallest merged into one, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def path(a, b):
	steps, i, j = "", 0, 0
	while i < len(a) or j < len(b):
		if j == len(b) or (i < len(a) and a[i] <= b[j]):
			steps, i = steps + "a", i + 1
		else:
			steps, j = steps + "b", j + 1
	return steps

def oracle(params, test):
	a, b = values(test)
	rule = params["rule"]
	if rule == "descending":
		return shown(sorted(a + b, reverse=True))
	if rule == "unique":
		return shown(sorted(set(a + b)))
	return shown(path(a, b))

def generate_tests(params, rng):
	descending = params["rule"] == "descending"
	pairs = [([1, 4], [2, 3]), ([2], [1, 2]), ([], []), ([1, 2], []), ([], [5]), ([1, 1, 3], [1, 2, 3, 3]),
		([-3, 0, 7], [-5, 0, 0, 9])]
	for _ in range(10):
		pairs.append(tuple(sorted(rng.randint(-9, 20) for _ in range(rng.randint(0, 6))) for _ in range(2)))
	if descending:
		pairs = [(a[::-1], b[::-1]) for a, b in pairs] + [([9, 4, 1], [8, 4])]
	return [case(list(a), list(b)) for a, b in pairs]

RULES = {
	"descending": ("list[int]", "a and b are sorted from the largest to the smallest value, and it\n"
		"returns a new list of all their values, sorted the same way"),
	"unique": ("list[int]", "a and b are sorted from the smallest to the largest value, and it\n"
		"returns a new list of their values sorted the same way, each value once"),
	"path": ("str", "a and b are sorted from the smallest to the largest value. Merging them\n"
		"takes, at each step, the smaller of the first values left in a and in b\n"
		"(the one of a when they are equal). It returns a string of one letter\n"
		"for each step: a when the value is taken from a, b when it is taken\n"
		"from b"),
}

EXERCISE = Exercise(
	name="merge_twist",
	language="python",
	kind="function",
	assignment_name="merge_${rule}",
	expected_files=("merge_${rule}.py",),
	allowed_functions=(),
	forbidden_calls=("sorted", "sort"),
	themes=("sorted_merge",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes two lists of ints, a and b, that may be empty:\n"
		"$rule.\n"
		"\n"
		"The given lists must not be changed. You may not use sorted() nor the\n"
		"sort() method of lists: go through the two lists side by side.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("merge_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(a: list[int], b: list[int]) -> {RULES[params['rule']][0]}:",
	examples=lambda params: {
		"descending": (case([9, 4, 1], [8, 4]), case([], [3])),
		"unique": (case([1, 1, 3], [1, 2, 3, 3]), case([], [])),
		"path": (case([1, 4], [2, 3]), case([2], [1, 2])),
	}[params["rule"]],
)
