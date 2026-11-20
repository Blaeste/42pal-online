"""edge_spare: an original Python model in the style of "find the edge that
closes a cycle in a graph".

The student writes a function about the edges of an undirected graph: its
number of groups, the edges of the only cycle of a tree with one more edge,
or the fewest edges to remove so that no cycle is left. The edge that can be
removed, the last one in the list, the real subject, is not one of the
rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def groups(n, edges):
	parent = list(range(n + 1))

	def root(node):
		while parent[node] != node:
			node = parent[node]
		return node

	count = n
	for a, b in edges:
		ra, rb = root(a), root(b)
		if ra != rb:
			parent[ra] = rb
			count -= 1
	return count

def cycle_edges(edges):
	# The edges of the cycle are those whose removal keeps the graph in one group.
	nodes = {node for edge in edges for node in edge}
	return [edge for index, edge in enumerate(edges)
		if groups(max(nodes), edges[:index] + edges[index + 1:]) == groups(max(nodes), edges)]

def oracle(params, test):
	rule = params["rule"]
	if rule == "cycle_edges":
		return shown(cycle_edges(*values(test)))
	n, edges = values(test)
	if rule == "components":
		return shown(groups(n, edges))
	return shown(len(edges) - (n - groups(n, edges)))

def random_tree_plus_one(rng):
	n = rng.randint(3, 8)
	edges = [[rng.randint(1, node - 1), node] for node in range(2, n + 1)]
	while True:
		a, b = rng.sample(range(1, n + 1), 2)
		if [a, b] not in edges and [b, a] not in edges:
			edges.insert(rng.randint(0, len(edges)), [a, b])
			break
	rng.shuffle(edges)
	return [edge[::-1] if rng.randint(0, 1) else edge for edge in edges]

def random_graph(rng):
	n = rng.randint(1, 8)
	edges = []
	for _ in range(rng.randint(0, n + 2)):
		a, b = rng.randint(1, n), rng.randint(1, n)
		if a != b and [a, b] not in edges and [b, a] not in edges:
			edges.append([a, b])
	return n, edges

def generate_tests(params, rng):
	rule = params["rule"]
	if rule == "cycle_edges":
		fixed = [[[1, 2], [2, 3], [3, 4], [4, 2], [1, 5]], [[1, 2], [1, 3], [2, 3]], [[2, 1], [3, 2], [4, 3], [1, 4]]]
		return [case(edges) for edges in fixed + [random_tree_plus_one(rng) for _ in range(10)]]
	fixed = [(5, [[1, 2], [3, 4]]), (4, [[1, 2], [2, 3], [3, 1], [1, 4], [2, 4]]), (1, []), (3, []),
		(3, [[1, 2], [2, 3], [3, 1]])]
	return [case(n, edges) for n, edges in fixed + [random_graph(rng) for _ in range(10)]]

RULES = {
	"components": ("n: int, edges: list[list[int]]", "int", "takes a number of nodes n (the\n"
		"nodes are 1 to n) and a list of edges, each one a pair [u, v], and returns\n"
		"the number of groups of the graph. Nodes linked by edges, directly or\n"
		"not, are in the same group; a node with no edge is a group alone"),
	"cycle_edges": ("edges: list[list[int]]", "list[list[int]]", "takes the edges of a graph\n"
		"that was a tree with nodes 1 to n (all linked, no cycle) and got one more\n"
		"edge: n edges, each one a pair [u, v]. The graph now holds exactly one\n"
		"cycle; the function returns the edges of that cycle, as given, in the\n"
		"order of the list"),
	"count": ("n: int, edges: list[list[int]]", "int", "takes a number of nodes n (the nodes\n"
		"are 1 to n) and a list of edges, each one a pair [u, v], and returns the\n"
		"fewest number of edges to remove so that the graph holds no cycle"),
}

EXERCISE = Exercise(
	name="edge_spare",
	language="python",
	kind="function",
	assignment_name="spare_${rule}",
	expected_files=("spare_${rule}.py",),
	allowed_functions=(),
	themes=("extra_edge",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that\n"
		"$rule.\n"
		"\n"
		"The graph is undirected: the edge [u, v] links u and v both ways. No edge\n"
		"links a node to itself, and no two edges link the same two nodes.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("spare_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"components": (case(5, [[1, 2], [3, 4]]), case(1, [])),
		"cycle_edges": (case([[1, 2], [2, 3], [3, 4], [4, 2], [1, 5]]),),
		"count": (case(4, [[1, 2], [2, 3], [3, 1], [1, 4], [2, 4]]), case(3, [])),
	}[params["rule"]],
)
