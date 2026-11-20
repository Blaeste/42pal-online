"""turn_find: an original Python model in the style of "tell whether a list
is a rotation of another".

The student writes a function that compares two lists through turnings:
the smallest turn that gives the second, all the turns that give it, or a
turning of the first list read backwards. Saying whether the second list is
a turning of the first, the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def turned(items, k):
	"""items turned k places to the right: the last k items come first."""
	return items[len(items) - k:] + items[:len(items) - k] if items else []

def all_steps(a, b):
	if len(a) != len(b):
		return []
	if not a:
		return [0]
	return [k for k in range(len(a)) if turned(a, k) == b]

def oracle(params, test):
	a, b = values(test)
	rule = params["rule"]
	if rule == "steps":
		steps = all_steps(a, b)
		return shown(steps[0] if steps else -1)
	if rule == "all_steps":
		return shown(all_steps(a, b))
	return shown(bool(all_steps(a[::-1], b)))

def generate_tests(params, rng):
	pairs = [([1, 2, 3, 4], [3, 4, 1, 2]), ([1, 2, 3], [3, 2, 1]), ([], []), ([1, 1, 1], [1, 1, 1]),
		([1, 2], [1, 2, 3]), ([1, 2, 3, 4], [2, 1, 4, 3]), ([1, 2, 3, 4], [1, 3, 2, 4]), ([5], [5]),
		([1, 2, 1, 2], [2, 1, 2, 1]), ([], [1])]
	for _ in range(10):
		a = [rng.randint(0, 3) for _ in range(rng.randint(1, 6))]
		pick = rng.randint(0, 3)
		if pick == 0:
			b = turned(a, rng.randrange(len(a)))
		elif pick == 1:
			b = turned(a[::-1], rng.randrange(len(a)))
		else:
			b = [rng.randint(0, 3) for _ in range(len(a))]
		pairs.append((a, b))
	return [case(a, b) for a, b in pairs]

RULES = {
	"steps": ("int", "the smallest number of places k (from 0) such that a turned k places to\n"
		"the right gives b; or -1 if there is none. Two empty lists give 0"),
	"all_steps": ("list[int]", "every number of places k, from 0 to the length of a minus 1,\n"
		"such that a turned k places to the right gives b, in increasing order (an\n"
		"empty list if there is none). Two empty lists give [0]"),
	"mirrored": ("bool", "True if b is the list a read backwards, then turned some number of\n"
		"places to the right (0 included), and False otherwise. Two empty lists\n"
		"give True"),
}

EXERCISE = Exercise(
	name="turn_find",
	language="python",
	kind="function",
	assignment_name="turn_${rule}",
	expected_files=("turn_${rule}.py",),
	allowed_functions=(),
	themes=("rotation_check",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes two lists of ints, a and b, and returns\n"
		"$rule.\n"
		"\n"
		"A list turned k places to the right has its last k items first, in their\n"
		"order, then the others: [1, 2, 3, 4] turned 1 place gives [4, 1, 2, 3].\n"
		"Lists of different lengths are never turnings of each other.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("turn_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(a: list[int], b: list[int]) -> {RULES[params['rule']][0]}:",
	examples=lambda params: {
		"steps": (case([1, 2, 3, 4], [3, 4, 1, 2]), case([1, 2, 3], [3, 2, 1])),
		"all_steps": (case([1, 2, 1, 2], [2, 1, 2, 1]), case([1, 2], [1, 2, 3])),
		"mirrored": (case([1, 2, 3, 4], [2, 1, 4, 3]), case([1, 2, 3, 4], [1, 3, 2, 4])),
	}[params["rule"]],
)
