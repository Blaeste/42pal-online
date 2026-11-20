"""cut_find: an original Python model in the style of "find the edges a
graph cannot lose".

The student writes a function about the nodes an undirected graph cannot
lose: those whose removal cuts it into more groups, or the number of groups
left without each node. The edges whose removal cuts the graph, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def nodes_of(graph):
	return sorted(set(graph) | {other for others in graph.values() for other in others})

def groups(graph, without=None):
	seen, count = {without}, 0
	for node in nodes_of(graph):
		if node in seen:
			continue
		count += 1
		todo = [node]
		seen.add(node)
		while todo:
			for other in graph.get(todo.pop(), []):
				if other not in seen:
					seen.add(other)
					todo.append(other)
	return count

def oracle(params, test):
	(graph,) = values(test)
	left = {node: groups(graph, node) for node in nodes_of(graph)}
	if params["rule"] == "groups":
		return shown(left)
	return shown([node for node, count in left.items() if count > groups(graph)])

def random_graph(rng):
	size = rng.randint(1, 8)
	graph = {node: [] for node in range(1, size + 1)}
	for _ in range(rng.randint(0, size + 2)):
		a, b = rng.randint(1, size), rng.randint(1, size)
		if a != b and b not in graph[a]:
			graph[a].append(b)
			graph[b].append(a)
	return graph

def generate_tests(params, rng):
	graphs = [{1: [2], 2: [1, 3, 4], 3: [2, 4], 4: [2, 3, 5], 5: [4]}, {}, {1: []}, {1: [2], 2: [1]},
		{1: [2], 2: [1, 3], 3: [2]}, {1: [2, 3], 2: [1, 3], 3: [1, 2]}, {1: [2], 2: [1], 3: [4], 4: [3]}]
	return [case(graph) for graph in graphs + [random_graph(rng) for _ in range(10)]]

RULES = {
	"points": ("cut_points", "list[int]", "the nodes whose removal, with their edges, leaves the\n"
		"graph in more groups than before, sorted in increasing order"),
	"groups": ("cut_groups", "dict[int, int]", "a dict that gives, for each node in increasing\n"
		"order, the number of groups of the graph without that node and its edges"),
}

EXERCISE = Exercise(
	name="cut_find",
	language="python",
	kind="function",
	assignment_name="cut_${rule}",
	expected_files=("cut_${rule}.py",),
	allowed_functions=(),
	themes=("graph_bridges",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that takes an undirected graph as a dict: each key is a\n"
		"node (an int) and its value the list of the nodes it is linked to; each\n"
		"edge is listed both ways, and no node is linked to itself. Nodes linked by\n"
		"edges, directly or not, are in the same group, and a node with no edge is a\n"
		"group alone. The function returns\n"
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
	harness=harness("cut_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(graph: dict[int, list[int]]) -> {RULES[params['rule']][1]}:",
	examples=(case({1: [2], 2: [1, 3, 4], 3: [2, 4], 4: [2, 3, 5], 5: [4]}), case({1: [2], 2: [1]})),
)
