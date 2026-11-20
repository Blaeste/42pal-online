"""need_order: an original Python model in the style of "order items so that
each comes after what it needs".

The student writes a function that reads a dict of packages and the
packages each one needs: the packages level by level, what to install for
one package, or the longest chain under each package. One installation
order of every package, the real subject, is not one of the rules.
"""

import heapq

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def needs(packages):
	"""The needs of each package, those that are not keys left out."""
	return {name: [need for need in wanted if need in packages] for name, wanted in packages.items()}

def levels(packages):
	graph, placed, result = needs(packages), set(), []
	while len(placed) < len(graph):
		level = sorted(name for name, wanted in graph.items()
			if name not in placed and all(need in placed for need in wanted))
		if not level:
			return None
		result.append(level)
		placed.update(level)
	return result

def install_for(packages, target):
	graph = needs(packages)
	wanted, stack = set(), [target]
	while stack:
		name = stack.pop()
		if name not in wanted:
			wanted.add(name)
			stack.extend(graph[name])
	order, done = [], set()
	ready = [name for name in wanted if not graph[name]]
	heapq.heapify(ready)
	while ready:
		name = heapq.heappop(ready)
		order.append(name)
		done.add(name)
		for other in wanted:
			if other not in done and other not in ready and all(need in done for need in graph[other]):
				heapq.heappush(ready, other)
	return order if len(order) == len(wanted) else None

def depth(packages):
	layers = levels(packages)
	if layers is None:
		return None
	graph, found = needs(packages), {}
	for level in layers:
		for name in level:
			found[name] = max((found[need] + 1 for need in graph[name]), default=0)
	return {name: found[name] for name in packages}

def oracle(params, test):
	rule = params["rule"]
	if rule == "install_for":
		packages, target = values(test)
		return shown(install_for(packages, target))
	(packages,) = values(test)
	return shown(levels(packages) if rule == "levels" else depth(packages))

def random_packages(rng):
	names = rng.sample(["app", "lib", "net", "core", "log", "db", "ui", "zip"], rng.randint(1, 6))
	packages = {}
	for index, name in enumerate(names):
		# Mostly needs among the names after it: few cycles.
		later = names[index + 1:] + (names[:index] if rng.randint(0, 5) == 0 else [])
		packages[name] = rng.sample(later, min(len(later), rng.randint(0, 2)))
	return packages

def generate_tests(params, rng):
	fixed = [{"app": ["lib", "net"], "lib": ["core"], "net": ["core"], "core": [], "tool": ["x"]},
		{"a": ["b"], "b": ["a"], "c": []}, {"solo": []}, {"x": ["x"]},
		{"b": ["a"], "a": [], "d": ["c", "b"], "c": ["a"]}]
	groups = fixed + [random_packages(rng) for _ in range(10)]
	if params["rule"] != "install_for":
		return [case(group) for group in groups + [{}]]
	targets = ["app", "c", "solo", "x", "d"] + [rng.choice(list(group)) for group in groups[5:]]
	return [case(group, target) for group, target in zip(groups, targets)] + [case(fixed[1], "a")]

RULES = {
	"levels": ("packages: dict[str, list[str]]", "list[list[str]] | None", "returns the packages\n"
		"level by level: the first level holds the packages that need nothing,\n"
		"the second one those that need only packages of the first level, and so\n"
		"on (each package on the first level it can be on). Each level is a list\n"
		"sorted in alphabetical order. If some packages can never be placed\n"
		"because they need each other, it returns None. An empty dict gives an\n"
		"empty list"),
	"install_for": ("packages: dict[str, list[str]], target: str", "list[str] | None",
		"returns the packages to install to get target, a key of the dict: the\n"
		"packages it needs, those they need, and so on, then target itself. Each\n"
		"one comes after all the packages it needs and, among the packages that\n"
		"could come next, the first in alphabetical order comes first. If some\n"
		"of these packages need each other, it returns None"),
	"depth": ("packages: dict[str, list[str]]", "dict[str, int] | None", "returns a dict that\n"
		"gives, for each package, the length of the longest chain of needs under\n"
		"it: 0 for a package that needs nothing, 1 for one that needs only\n"
		"packages that need nothing, and so on. Its keys come in the order of the\n"
		"given dict. If some packages need each other, it returns None"),
}

EXERCISE = Exercise(
	name="need_order",
	language="python",
	kind="function",
	assignment_name="need_${rule}",
	expected_files=("need_${rule}.py",),
	allowed_functions=(),
	themes=("dependency_order",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a dict of packages: each key is the name of a\n"
		"package, and its value the list of the packages it needs, which must be\n"
		"installed before it. A needed package that is not a key of the dict is\n"
		"ignored. The function\n"
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
	harness=harness("need_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"levels": (case({"app": ["lib", "net"], "lib": ["os"], "net": ["os"], "os": []}),
			case({"a": ["b"], "b": ["a"]})),
		"install_for": (case({"e": ["c", "b"], "c": ["a"], "b": ["a"], "a": []}, "e"),
			case({"a": ["b"], "b": ["a"], "c": []}, "c")),
		"depth": (case({"app": ["lib"], "lib": ["os"], "os": [], "tool": ["x"]}),),
	}[params["rule"]],
)
