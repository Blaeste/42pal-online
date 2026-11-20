"""Reference solution of need_order, for every variant: one function each."""

def _clean(packages):
	return {name: [need for need in wanted if need in packages] for name, wanted in packages.items()}

def need_levels(packages):
	graph = _clean(packages)
	level_of = {}
	changed = True
	while changed:
		changed = False
		for name, wanted in graph.items():
			if name not in level_of and all(need in level_of for need in wanted):
				level_of[name] = max([level_of[need] + 1 for need in wanted] + [0])
				changed = True
	if len(level_of) < len(graph):
		return None
	result = [[] for _ in range(max(level_of.values()) + 1)] if level_of else []
	for name in sorted(level_of):
		result[level_of[name]].append(name)
	return result

def need_depth(packages):
	if need_levels(packages) is None:
		return None
	graph = _clean(packages)
	memo = {}

	def longest(name):
		if name not in memo:
			memo[name] = max([longest(need) + 1 for need in graph[name]] + [0])
		return memo[name]

	return {name: longest(name) for name in packages}

def need_install_for(packages, target):
	graph = _clean(packages)
	wanted = []
	todo = [target]
	while todo:
		name = todo.pop(0)
		if name not in wanted:
			wanted.append(name)
			todo.extend(graph[name])
	order = []
	while len(order) < len(wanted):
		ready = [name for name in wanted
			if name not in order and all(need in order for need in graph[name])]
		if not ready:
			return None
		order.append(min(ready))
	return order
