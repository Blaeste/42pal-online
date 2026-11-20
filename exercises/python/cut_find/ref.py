"""Reference solution of cut_find, for every variant: one function each.

cut_points uses the times of a depth-first search (Tarjan): a node cuts the
graph when a child cannot climb above it; cut_groups counts the groups left
without each node, with the same search.
"""

def _nodes(graph):
	found = set(graph)
	for others in graph.values():
		found.update(others)
	return sorted(found)

def cut_points(graph):
	time = {}
	low = {}
	cuts = set()

	def search(node, parent):
		time[node] = low[node] = len(time)
		children = 0
		for other in graph.get(node, []):
			if other == parent:
				continue
			if other in time:
				low[node] = min(low[node], time[other])
				continue
			children += 1
			search(other, node)
			low[node] = min(low[node], low[other])
			if parent is not None and low[other] >= time[node]:
				cuts.add(node)
		if parent is None and children > 1:
			cuts.add(node)

	for node in _nodes(graph):
		if node not in time:
			search(node, None)
	return sorted(cuts)

def _count(graph, gone):
	seen = {gone}
	count = 0
	for node in _nodes(graph):
		if node in seen:
			continue
		count += 1
		stack = [node]
		seen.add(node)
		while stack:
			for other in graph.get(stack.pop(), []):
				if other not in seen:
					seen.add(other)
					stack.append(other)
	return count

def cut_groups(graph):
	return {node: _count(graph, node) for node in _nodes(graph)}
