"""loop_seek: an original Python model in the style of "find a cycle in a
directed graph".

The student writes a function that looks for cycles: the first cycle found
by a depth-first search, a cycle in an undirected graph, or every node that
is on a cycle. Saying whether a directed graph has a cycle, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def nodes_of(graph):
	return sorted(set(graph) | {other for others in graph.values() for other in others})

def find(graph):
	done = set()

	def visit(node, path):
		path.append(node)
		for other in graph.get(node, []):
			if other in path:
				return path[path.index(other):]
			if other not in done:
				cycle = visit(other, path)
				if cycle:
					return cycle
		path.pop()
		done.add(node)
		return None

	for node in nodes_of(graph):
		if node not in done:
			cycle = visit(node, [])
			if cycle:
				return cycle
	return None

def reaches(graph, start, goal):
	seen, todo = set(), list(graph.get(start, []))
	while todo:
		node = todo.pop()
		if node == goal:
			return True
		if node not in seen:
			seen.add(node)
			todo.extend(graph.get(node, []))
	return False

def undirected_cycle(graph):
	parent = {node: node for node in nodes_of(graph)}

	def root(node):
		while parent[node] != node:
			node = parent[node]
		return node

	for node in sorted(graph):
		for other in graph[node]:
			if other == node:
				return True
			if node < other:
				a, b = root(node), root(other)
				if a == b:
					return True
				parent[a] = b
	return False

def oracle(params, test):
	(graph,) = values(test)
	rule = params["rule"]
	if rule == "find":
		return shown(find(graph))
	if rule == "on_cycle":
		return shown([node for node in nodes_of(graph) if reaches(graph, node, node)])
	return shown(undirected_cycle(graph))

def random_graph(rng, undirected):
	size = rng.randint(1, 6)
	graph = {node: [] for node in range(1, size + 1)}
	for _ in range(rng.randint(0, size + 1)):
		a, b = rng.randint(1, size), rng.randint(1, size)
		if undirected:
			if a != b and b not in graph[a]:
				graph[a].append(b)
				graph[b].append(a)
		elif b not in graph[a]:
			graph[a].append(b)
	return graph

def generate_tests(params, rng):
	if params["rule"] == "undirected":
		graphs = [{1: [2], 2: [1, 3], 3: [2]}, {1: [2, 3], 2: [1, 3], 3: [1, 2]}, {1: [1]}, {}, {4: []},
			{1: [2], 2: [1], 3: [4, 5], 4: [3, 5], 5: [3, 4]}]
	else:
		graphs = [{1: [2], 2: [3], 3: [1, 4], 4: [], 5: [5]}, {5: [5]}, {1: [2], 2: [3], 3: []}, {},
			{2: [1], 1: [3], 3: [2]}, {1: [2, 3], 3: [4], 4: [3]}, {1: [2]}]
	graphs += [random_graph(rng, params["rule"] == "undirected") for _ in range(10)]
	return [case(graph) for graph in graphs]

RULES = {
	"find": ("list[int] | None", "returns a cycle, as a list of nodes, found by this depth-first\n"
		"search (None if there is no cycle):\n"
		"- it starts from each node in increasing order, skipping the nodes already\n"
		"searched from;\n"
		"- it follows the edges of a node in their given order;\n"
		"- the first time it reaches a node that is on its current path, the cycle\n"
		"is that path, from that node to the current one"),
	"undirected": ("bool", "the graph is undirected: each edge is listed in both directions\n"
		"(1 in the list of 2, and 2 in the list of 1), and no edge is listed\n"
		"twice. It returns True if the graph holds a cycle, a node with an edge\n"
		"to itself being one, and False otherwise"),
	"on_cycle": ("list[int]", "returns the nodes that are on a cycle (those that can reach\n"
		"themselves through one edge or more), sorted in increasing order"),
}

EXERCISE = Exercise(
	name="loop_seek",
	language="python",
	kind="function",
	assignment_name="loop_${rule}",
	expected_files=("loop_${rule}.py",),
	allowed_functions=(),
	themes=("graph_cycle",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a graph as a dict: each key is a node (an int)\n"
		"and its value the list of the nodes its edges go to. A node may also\n"
		"appear only in the lists. The function\n"
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
	harness=harness("loop_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(graph: dict[int, list[int]]) -> {RULES[params['rule']][0]}:",
	examples=lambda params: {
		"find": (case({1: [2], 2: [3], 3: [1, 4], 4: [], 5: [5]}), case({1: [2], 2: [3], 3: []})),
		"undirected": (case({1: [2], 2: [1, 3], 3: [2]}), case({1: [2, 3], 2: [1, 3], 3: [1, 2]})),
		"on_cycle": (case({1: [2], 2: [3], 3: [1, 4], 4: [], 5: [5]}),),
	}[params["rule"]],
)
