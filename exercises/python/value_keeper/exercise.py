"""value_keeper: an original Python model in the style of "write a class that
keeps the most recently used values".

The student writes a class Keeper that keeps a fixed number of keys and
their values, and makes room by taking out the key used the fewest times,
the key that came in first, or the key used last. Taking out the key used
the longest ago, the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import class_call, class_case, class_harness, class_values, shown

def run(rule, capacity, steps):
	values, uses, last, came, results = {}, {}, {}, {}, []
	for clock, (method, *args) in enumerate(steps):
		key = args[0]
		if method == "get":
			if key in values:
				uses[key] += 1
				last[key] = clock
				results.append(values[key])
			else:
				results.append(-1)
			continue
		if key not in values and len(values) == capacity:
			if rule == "lfu":
				out = min(values, key=lambda k: (uses[k], last[k]))
			elif rule == "fifo":
				out = min(values, key=lambda k: came[k])
			else:
				out = max(values, key=lambda k: last[k])
			for table in (values, uses, last, came):
				del table[out]
		if key not in values:
			uses[key], came[key] = 0, clock
		values[key] = args[1]
		uses[key] += 1
		last[key] = clock
		results.append(None)
	return results

def oracle(params, test):
	init, steps = class_values(test)
	return shown(run(params["rule"], init[0], steps))

FIXED = {
	"lfu": [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 2], ["get", 3], ["put", 4, 4],
		["get", 1], ["get", 3], ["get", 4]],
	"fifo": [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 1], ["put", 2, 20],
		["put", 4, 4], ["get", 2], ["get", 3]],
	"mru": [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 1], ["get", 2], ["get", 3],
		["put", 4, 4], ["get", 2]],
}

def generate_tests(params, rng):
	rule = params["rule"]
	tests = [class_case([2], FIXED[rule]), class_case([1], [["get", 5], ["put", 5, 50], ["put", 6, 60],
		["get", 5], ["get", 6]])]
	for _ in range(10):
		steps = []
		for _ in range(rng.randint(4, 14)):
			key = rng.randint(1, 5)
			steps.append(["get", key] if rng.randint(0, 1) else ["put", key, rng.randint(0, 99)])
		tests.append(class_case([rng.randint(1, 3)], steps))
	return tests

RULES = {
	"lfu": "the key used the fewest times goes out; among keys used as many times,\n"
		"the one whose last use is the oldest. A use is a get that finds the key\n"
		"or a put of it (the put that brings a key in is its first use)",
	"fifo": "the key that came in first goes out. A get changes nothing, and a put of\n"
		"a key already kept changes its value but not its place",
	"mru": "the key used last goes out, before the new key comes in. A use is a get\n"
		"that finds the key or a put of it",
}

EXERCISE = Exercise(
	name="value_keeper",
	language="python",
	kind="function",
	assignment_name="keeper_${rule}",
	expected_files=("keeper_${rule}.py",),
	allowed_functions=(),
	themes=("lru_cache",),
	params=(Param("rule", tuple(RULES), RULES),),
	subject=(
		"Write a class named Keeper that keeps at most capacity keys (ints), each\n"
		"with a value (an int). Its methods:\n"
		"- Keeper(capacity) makes an empty keeper (capacity is at least 1);\n"
		"- get(key) returns the value of key, or -1 if key is not kept;\n"
		"- put(key, value) gives key the value value, and returns None.\n"
		"\n"
		"When a new key comes in and the keeper is full, one key goes out first:\n"
		"$rule.\n"
		"\n"
		"The methods return their results and print nothing.\n"
		"\n"
		"Your class must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=class_harness("keeper_${rule}", "Keeper"),
	call=class_call("Keeper"),
	prototype=lambda name, params: ("class Keeper:\n    def __init__(self, capacity: int) -> None:\n"
		"    def get(self, key: int) -> int:\n    def put(self, key: int, value: int) -> None:"),
	examples=(class_case([2], [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 1]]),
		class_case([2], [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 2]])),
)
