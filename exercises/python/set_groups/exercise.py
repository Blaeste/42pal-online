"""set_groups: an original Python model in the style of "write a class that
joins sets and finds their leaders".

The student writes a class Groups that joins elements into groups: with the
size of each group and the number of groups, with names instead of
numbers, or with an undo of the last joins. find, union and connected with
path compression and union by rank, the real subject, is not one of the
rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import class_call, class_case, class_harness, class_values, shown

def run(rule, init, steps):
	"""The results of the calls, with each group kept as a plain set."""
	group_of = {element: {element} for element in range(init[0])} if init else {}
	history, results = [], []

	def group(element):
		group_of.setdefault(element, {element})
		return group_of[element]

	def join(a, b):
		ga, gb = group(a), group(b)
		if ga is gb:
			return False
		history.append((ga, gb))
		merged = ga | gb
		for element in merged:
			group_of[element] = merged
		return True

	for method, *args in steps:
		if method in ("union", "join"):
			results.append(join(*args))
		elif method in ("together", "same"):
			results.append(group(args[0]) is group(args[1]))
		elif method == "size":
			results.append(len(group(args[0])))
		elif method == "count":
			results.append(len({id(members) for members in group_of.values()}))
		elif method == "members":
			results.append(sorted(group(args[0])))
		else:
			if not history:
				results.append(False)
				continue
			ga, gb = history.pop()
			for members in (ga, gb):
				for element in members:
					group_of[element] = members
			results.append(True)
	return results

def oracle(params, test):
	init, steps = class_values(test)
	return shown(run(params["rule"], init, steps))

NAMES = ["ann", "bob", "cid", "dan", "eve"]

def random_steps(rng, rule, n):
	steps = []
	for _ in range(rng.randint(3, 12)):
		if rule == "names":
			method = rng.choice(["join", "join", "same", "members"])
			args = [rng.choice(NAMES) for _ in range(1 if method == "members" else 2)]
		elif rule == "sizes":
			method = rng.choice(["union", "union", "size", "count"])
			args = [rng.randrange(n) for _ in range({"union": 2, "size": 1, "count": 0}[method])]
		else:
			method = rng.choice(["union", "union", "together", "undo"])
			args = [rng.randrange(n) for _ in range(0 if method == "undo" else 2)]
		steps.append([method, *args])
	return steps

FIXED = {
	"sizes": [([5], [["union", 0, 1], ["union", 1, 2], ["union", 0, 2], ["size", 2], ["size", 4], ["count"]]),
		([1], [["count"], ["union", 0, 0], ["size", 0]])],
	"names": [([], [["join", "ann", "bob"], ["join", "cid", "dan"], ["same", "ann", "dan"],
		["join", "bob", "dan"], ["members", "cid"], ["same", "eve", "eve"], ["members", "eve"]])],
	"undo": [([4], [["union", 0, 1], ["union", 2, 3], ["union", 0, 1], ["together", 0, 3], ["union", 1, 3],
		["together", 0, 2], ["undo"], ["together", 0, 2], ["together", 2, 3], ["undo"], ["undo"], ["undo"],
		["together", 0, 1]])],
}

def generate_tests(params, rng):
	rule = params["rule"]
	tests = [class_case(init, steps) for init, steps in FIXED[rule]]
	for _ in range(10):
		n = rng.randint(2, 6)
		tests.append(class_case([] if rule == "names" else [n], random_steps(rng, rule, n)))
	return tests

RULES = {
	"sizes": ("Its methods:\n"
		"- Groups(n) makes n elements, numbered from 0 to n - 1, each in a group of\n"
		"its own;\n"
		"- union(a, b) joins the groups of a and b and returns True, or returns\n"
		"False if they already were in the same group;\n"
		"- size(x) returns the number of elements in the group of x;\n"
		"- count() returns the number of groups.",
		"    def __init__(self, n: int) -> None:\n    def union(self, a: int, b: int) -> bool:\n"
		"    def size(self, x: int) -> int:\n    def count(self) -> int:"),
	"names": ("The elements are names (strings): a name used for the first time is a\n"
		"new element, in a group of its own. Its methods:\n"
		"- Groups() starts with no element;\n"
		"- join(a, b) joins the groups of a and b and returns True, or returns False\n"
		"if they already were in the same group;\n"
		"- same(a, b) returns True if a and b are in the same group, False\n"
		"otherwise;\n"
		"- members(a) returns the names of the group of a, in alphabetical order.",
		"    def __init__(self) -> None:\n    def join(self, a: str, b: str) -> bool:\n"
		"    def same(self, a: str, b: str) -> bool:\n    def members(self, a: str) -> list[str]:"),
	"undo": ("Its methods:\n"
		"- Groups(n) makes n elements, numbered from 0 to n - 1, each in a group of\n"
		"its own;\n"
		"- union(a, b) joins the groups of a and b and returns True, or returns\n"
		"False if they already were in the same group (that union changes\n"
		"nothing);\n"
		"- together(a, b) returns True if a and b are in the same group, False\n"
		"otherwise;\n"
		"- undo() cancels the last union that joined two groups and is not\n"
		"cancelled yet, so that these two groups are apart again, and returns True;\n"
		"it returns False if there is none.",
		"    def __init__(self, n: int) -> None:\n    def union(self, a: int, b: int) -> bool:\n"
		"    def together(self, a: int, b: int) -> bool:\n    def undo(self) -> bool:"),
}

EXERCISE = Exercise(
	name="set_groups",
	language="python",
	kind="function",
	assignment_name="groups_${rule}",
	expected_files=("groups_${rule}.py",),
	allowed_functions=(),
	themes=("disjoint_sets",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (text, _) in RULES.items()}),),
	subject=(
		"Write a class named Groups that keeps elements in groups: each element is\n"
		"in exactly one group, and joining two elements merges their groups.\n"
		"Keep, for each element, a parent that leads to the leader of its group.\n"
		"\n"
		"$rule\n"
		"\n"
		"The methods return their results and print nothing.\n"
		"\n"
		"Your class must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=class_harness("groups_${rule}", "Groups"),
	call=class_call("Groups"),
	prototype=lambda name, params: "class Groups:\n" + RULES[params["rule"]][1],
	examples=lambda params: {
		"sizes": (class_case([5], [["union", 0, 1], ["union", 1, 2], ["union", 0, 2], ["size", 2]]),
			class_case([5], [["union", 0, 1], ["count"]])),
		"names": (class_case([], [["join", "ann", "bob"], ["same", "bob", "ann"], ["members", "ann"]]),),
		"undo": (class_case([3], [["union", 0, 1], ["together", 0, 1], ["undo"], ["together", 0, 1]]),),
	}[params["rule"]],
)
