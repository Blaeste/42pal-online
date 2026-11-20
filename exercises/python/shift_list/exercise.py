"""shift_list: an original Python model in the style of "move the items of a
list around".

The student writes a function that returns a new list: turned to the left
by k places, reversed by blocks of k items, or turned to the right by k
places for the values from 0 only, the negative ones staying in their
places. Turning the whole list to the right, the real subject, is not one
of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def moved(items, k, rule):
	if rule == "left":
		k = k % len(items) if items else 0
		return items[k:] + items[:k]
	if rule == "blocks":
		return [item for start in range(0, len(items), k) for item in items[start:start + k][::-1]]
	places = [index for index, item in enumerate(items) if item >= 0]
	kept = [items[index] for index in places]
	if kept:
		k %= len(kept)
		kept = kept[len(kept) - k:] + kept[:len(kept) - k]
	result = list(items)
	for index, item in zip(places, kept):
		result[index] = item
	return result

def oracle(params, test):
	items, k = values(test)
	return shown(moved(items, k, params["rule"]))

def generate_tests(params, rng):
	low = 1 if params["rule"] == "blocks" else 0
	pairs = [([1, 2, 3, 4], 5), ([], 3), ([1, 2, 3, 4, 5, 6, 7], 3), ([1, -1, 2, 3, -5], 1), ([7], 1),
		([1, 2, 3], 3), ([-1, -2], 4), ([0, -3, 5], 2), ([1, 2, 3, 4], 1)]
	for _ in range(10):
		pairs.append(([rng.randint(-5, 9) for _ in range(rng.randint(0, 8))], rng.randint(low, 9)))
	return [case(items, k) for items, k in pairs]

EXERCISE = Exercise(
	name="shift_list",
	language="python",
	kind="function",
	assignment_name="shift_${rule}",
	expected_files=("shift_${rule}.py",),
	allowed_functions=(),
	themes=("list_rotate",),
	params=(
		Param("rule", ("left", "blocks", "keep_negatives"), {
			"left": "the items turned to the left by k places: the first k items go to the\n"
				"end, in their order. k may be larger than the length of the list:\n"
				"turning by the length gives the list back",
			"blocks": "the items reversed by blocks of k items (k is at least 1): the first k\n"
				"items in reverse order, then the next k items in reverse order, and so\n"
				"on; the last block may have fewer items",
			"keep_negatives": "the values from 0 turned to the right by k places among themselves:\n"
				"the last k of them come first, in their order, and they take the places\n"
				"where values from 0 were. The negative values stay in their places",
		}),
	),
	subject=(
		"Write a function that takes a list of ints and an int k from 0, and\n"
		"returns a new list with\n"
		"$rule.\n"
		"\n"
		"The given list must not be changed, and an empty list gives an empty list.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(items: list[int], k: int) -> list[int]:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("shift_${rule}"),
	call=call,
	examples=lambda params: {
		"left": (case([1, 2, 3, 4], 1), case([1, 2, 3, 4], 5)),
		"blocks": (case([1, 2, 3, 4, 5, 6, 7], 3), case([7], 1)),
		"keep_negatives": (case([1, -1, 2, 3, -5], 1), case([0, -3, 5], 2)),
	}[params["rule"]],
)
