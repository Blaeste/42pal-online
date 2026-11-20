"""top_heap: an original Python model in the style of "write a class that
keeps the smallest value on top".

The student writes a class Heap, a binary heap kept in a Python list: one
with the largest value on top, one that gives the k-th largest value added
so far, or one that gives the median of the values added, without sorted(),
sort(), min() nor max(). The heap with the smallest value on top, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import class_call, class_case, class_harness, class_values, shown

def run(rule, init, steps):
	items, results = [], []
	for method, *args in steps:
		if method in ("push", "add"):
			items.append(args[0])
			results.append(None)
			continue
		ordered = sorted(items, reverse=True)
		if method == "size":
			results.append(len(items))
		elif method in ("peek", "pop"):
			results.append(ordered[0] if items else None)
			if items and method == "pop":
				items.remove(ordered[0])
		elif method == "kth":
			results.append(ordered[init[0] - 1] if len(items) >= init[0] else None)
		else:
			results.append(sorted(items)[(len(items) - 1) // 2] if items else None)
	return results

def oracle(params, test):
	init, steps = class_values(test)
	return shown(run(params["rule"], init, steps))

FIXED = {
	"max_heap": ([], [["push", 3], ["push", 9], ["push", 1], ["peek"], ["pop"], ["size"], ["pop"], ["pop"],
		["pop"], ["peek"]]),
	"k_largest": ([2], [["kth"], ["add", 5], ["kth"], ["add", 1], ["kth"], ["add", 8], ["kth"], ["add", 8],
		["kth"]]),
	"median": ([], [["median"], ["add", 5], ["median"], ["add", 1], ["median"], ["add", 9], ["median"],
		["add", 3], ["median"]]),
}

QUESTIONS = {"max_heap": ["pop", "peek", "size"], "k_largest": ["kth"], "median": ["median"]}

def generate_tests(params, rng):
	rule = params["rule"]
	tests = [class_case(*FIXED[rule])]
	adding = "push" if rule == "max_heap" else "add"
	for _ in range(10):
		steps = [[adding, rng.randint(-20, 20)] if rng.randint(0, 2) else [rng.choice(QUESTIONS[rule])]
			for _ in range(rng.randint(5, 25))]
		tests.append(class_case([rng.randint(1, 3)] if rule == "k_largest" else [], steps))
	return tests

RULES = {
	"max_heap": ("Its methods:\n"
		"- Heap() makes an empty heap whose top is its largest value;\n"
		"- push(value) adds value;\n"
		"- pop() takes the largest value out and returns it, or returns None if the\n"
		"heap is empty;\n"
		"- peek() returns the largest value without taking it out, or None if the\n"
		"heap is empty;\n"
		"- size() returns the number of values in the heap.",
		"    def __init__(self) -> None:\n    def push(self, value: int) -> None:\n"
		"    def pop(self) -> int | None:\n    def peek(self) -> int | None:\n    def size(self) -> int:"),
	"k_largest": ("Its methods:\n"
		"- Heap(k) makes an empty heap that keeps the k largest values added (k is\n"
		"at least 1), the smallest of them on top;\n"
		"- add(value) adds value;\n"
		"- kth() returns the k-th largest value added so far (a value added several\n"
		"times counts each time), or None if fewer than k values were added.",
		"    def __init__(self, k: int) -> None:\n    def add(self, value: int) -> None:\n"
		"    def kth(self) -> int | None:"),
	"median": ("It keeps two heaps: the smaller half of the values, with its largest\n"
		"value on top, and the larger half, with its smallest value on top. Its\n"
		"methods:\n"
		"- Heap() makes an empty heap;\n"
		"- add(value) adds value;\n"
		"- median() returns the value in the middle of all the values added, as if\n"
		"they were sorted (for an even number of values, the smaller of the two in\n"
		"the middle), or None if no value was added.",
		"    def __init__(self) -> None:\n    def add(self, value: int) -> None:\n"
		"    def median(self) -> int | None:"),
}

EXERCISE = Exercise(
	name="top_heap",
	language="python",
	kind="function",
	assignment_name="heap_${rule}",
	expected_files=("heap_${rule}.py",),
	allowed_functions=(),
	forbidden_calls=("sorted", "sort", "min", "max"),
	themes=("binary_heap",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (text, _) in RULES.items()}),),
	subject=(
		"Write a class named Heap, a binary heap kept in a Python list: the value at\n"
		"index i has its children at the indexes 2 * i + 1 and 2 * i + 2, and the\n"
		"top is at index 0. A value added goes up from the end of the list, and the\n"
		"value that replaces the top goes down, each time swapped with a parent or\n"
		"a child.\n"
		"\n"
		"$rule\n"
		"\n"
		"You may not use sorted(), sort(), min() nor max(), nor import anything.\n"
		"The methods return their results and print nothing.\n"
		"\n"
		"Your class must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=class_harness("heap_${rule}", "Heap"),
	call=class_call("Heap"),
	prototype=lambda name, params: "class Heap:\n" + RULES[params["rule"]][1],
	examples=lambda params: {
		"max_heap": (class_case([], [["push", 3], ["push", 9], ["push", 1], ["pop"], ["peek"], ["size"]]),),
		"k_largest": (class_case([2], [["add", 5], ["kth"], ["add", 1], ["kth"], ["add", 8], ["kth"]]),),
		"median": (class_case([], [["add", 5], ["add", 1], ["median"], ["add", 9], ["median"]]),),
	}[params["rule"]],
)
