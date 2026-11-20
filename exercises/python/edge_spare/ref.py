"""Reference solution of edge_spare, for every variant: one function each."""

def _links(edges):
	links = {}
	for a, b in edges:
		links.setdefault(a, []).append(b)
		links.setdefault(b, []).append(a)
	return links

def spare_components(n, edges):
	links = _links(edges)
	seen = set()
	count = 0
	for node in range(1, n + 1):
		if node in seen:
			continue
		count += 1
		todo = [node]
		seen.add(node)
		while todo:
			for other in links.get(todo.pop(), []):
				if other not in seen:
					seen.add(other)
					todo.append(other)
	return count

def spare_count(n, edges):
	return len(edges) - n + spare_components(n, edges)

def spare_cycle_edges(edges):
	# Take away the leaves again and again: only the cycle is left.
	links = {node: set(others) for node, others in _links(edges).items()}
	leaves = [node for node, others in links.items() if len(others) == 1]
	while leaves:
		leaf = leaves.pop()
		for other in links[leaf]:
			links[other].discard(leaf)
			if len(links[other]) == 1:
				leaves.append(other)
		links[leaf] = set()
	return [[a, b] for a, b in edges if b in links[a]]
