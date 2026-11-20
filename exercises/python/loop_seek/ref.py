"""Reference solution of loop_seek, for every variant: one function each."""

def _all_nodes(graph):
	nodes = set(graph)
	for others in graph.values():
		nodes.update(others)
	return sorted(nodes)

def loop_find(graph):
	# 0: not seen, 1: on the current path, 2: done.
	state = {node: 0 for node in _all_nodes(graph)}
	path = []

	def search(node):
		state[node] = 1
		path.append(node)
		for other in graph.get(node, []):
			if state[other] == 1:
				return path[path.index(other):]
			if state[other] == 0:
				found = search(other)
				if found is not None:
					return found
		state[node] = 2
		path.pop()
		return None

	for node in _all_nodes(graph):
		if state[node] == 0:
			found = search(node)
			if found is not None:
				return found
	return None

def loop_undirected(graph):
	seen = set()
	for start in _all_nodes(graph):
		if start in seen:
			continue
		# A walk that remembers where it came from: another way back is a cycle.
		todo = [(start, None)]
		seen.add(start)
		while todo:
			node, came_from = todo.pop()
			for other in graph.get(node, []):
				if other == node:
					return True
				if other == came_from:
					continue
				if other in seen:
					return True
				seen.add(other)
				todo.append((other, node))
	return False

def loop_on_cycle(graph):
	result = []
	for node in _all_nodes(graph):
		seen = set()
		todo = list(graph.get(node, []))
		while todo:
			current = todo.pop()
			if current == node:
				result.append(node)
				break
			if current not in seen:
				seen.add(current)
				todo.extend(graph.get(current, []))
	return result
