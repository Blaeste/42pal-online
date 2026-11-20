"""task_plan: an original Python model in the style of "order tasks that
depend on each other".

The student writes a function about tasks and their prerequisites: the
fewest rounds when the tasks ready are done together, every task needed
before one task, or an order that takes the largest ready task first. An
order that takes the smallest ready task first, the real subject, is not
one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def before_of(n, prereqs):
	before = {task: set() for task in range(n)}
	for task, needed in prereqs:
		before[task].add(needed)
	return before

def rounds(n, prereqs):
	before, done, count = before_of(n, prereqs), set(), 0
	while len(done) < n:
		ready = {task for task in range(n) if task not in done and before[task] <= done}
		if not ready:
			return -1
		done |= ready
		count += 1
	return count

def largest_first(n, prereqs):
	before, order = before_of(n, prereqs), []
	while len(order) < n:
		ready = [task for task in range(n) if task not in order and before[task] <= set(order)]
		if not ready:
			return []
		order.append(max(ready))
	return order

def ancestors(n, prereqs, task):
	before, found, todo = before_of(n, prereqs), set(), [task]
	while todo:
		for needed in before[todo.pop()]:
			if needed not in found:
				found.add(needed)
				todo.append(needed)
	return sorted(found)

def oracle(params, test):
	rule = params["rule"]
	if rule == "ancestors":
		return shown(ancestors(*values(test)))
	return shown((rounds if rule == "rounds" else largest_first)(*values(test)))

def random_prereqs(rng, n, acyclic):
	pairs = []
	for _ in range(rng.randint(0, n + 2)):
		a, b = rng.randrange(n), rng.randrange(n)
		if acyclic:
			a, b = max(a, b), min(a, b)
		if a != b and [a, b] not in pairs:
			pairs.append([a, b])
	return pairs

def generate_tests(params, rng):
	rule = params["rule"]
	fixed = [(4, [[1, 0], [2, 0], [3, 1], [3, 2]]), (0, []), (3, []), (5, [[0, 4], [4, 3], [3, 2]]),
		(4, [[3, 0], [3, 1], [2, 3]])]
	if rule == "ancestors":
		tests = [case(n, prereqs, task) for (n, prereqs), task in zip(fixed[:1] * 2 + fixed[3:], [3, 0, 0, 2])]
		for _ in range(10):
			n = rng.randint(1, 7)
			tests.append(case(n, random_prereqs(rng, n, True), rng.randrange(n)))
		return tests
	fixed += [(2, [[0, 1], [1, 0]]), (3, [[0, 1], [1, 2], [2, 1]])]
	tests = [case(n, prereqs) for n, prereqs in fixed]
	for _ in range(10):
		n = rng.randint(1, 7)
		tests.append(case(n, random_prereqs(rng, n, rng.randint(0, 3) > 0)))
	return tests

RULES = {
	"rounds": ("n: int, prereqs: list[list[int]]", "int", "returns the fewest number of rounds\n"
		"to do all the tasks, when each round does at the same time every task\n"
		"whose prerequisites are all done; -1 if the tasks can never all be done\n"
		"(some of them wait for each other), and 0 when n is 0"),
	"ancestors": ("n: int, prereqs: list[list[int]], task: int", "list[int]", "also takes a\n"
		"task, and returns the tasks that must be done before it: its\n"
		"prerequisites, theirs, and so on, sorted in increasing order. The\n"
		"prerequisites never wait for each other"),
	"largest_first": ("n: int, prereqs: list[list[int]]", "list[int]", "returns an order to do\n"
		"all the tasks one by one: each time, the task of largest number among\n"
		"those whose prerequisites are all done. If the tasks can never all be\n"
		"done (some of them wait for each other), it returns an empty list"),
}

EXERCISE = Exercise(
	name="task_plan",
	language="python",
	kind="function",
	assignment_name="plan_${rule}",
	expected_files=("plan_${rule}.py",),
	allowed_functions=(),
	themes=("task_schedule",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that takes n, a number of tasks numbered from 0 to n - 1,\n"
		"and a list of prerequisites: each one is a pair [a, b] that means task b\n"
		"must be done before task a. The function\n"
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
	harness=harness("plan_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"rounds": (case(4, [[1, 0], [2, 0], [3, 1], [3, 2]]), case(2, [[0, 1], [1, 0]])),
		"ancestors": (case(4, [[1, 0], [2, 0], [3, 1], [3, 2]], 3),),
		"largest_first": (case(4, [[1, 0], [2, 0], [3, 1], [3, 2]]), case(2, [[0, 1], [1, 0]])),
	}[params["rule"]],
)
