"""Reference solution of task_plan, for every variant: one function each.

The counts of prerequisites left, like Kahn's algorithm.
"""

def _graph(n, prereqs):
	waiting = [0] * n
	unlocks = [[] for _ in range(n)]
	for task, needed in prereqs:
		waiting[task] += 1
		unlocks[needed].append(task)
	return waiting, unlocks

def plan_rounds(n, prereqs):
	waiting, unlocks = _graph(n, prereqs)
	current = [task for task in range(n) if waiting[task] == 0]
	done = 0
	count = 0
	while current:
		count += 1
		done += len(current)
		following = []
		for task in current:
			for other in unlocks[task]:
				waiting[other] -= 1
				if waiting[other] == 0:
					following.append(other)
		current = following
	return count if done == n else -1

def plan_largest_first(n, prereqs):
	waiting, unlocks = _graph(n, prereqs)
	ready = [task for task in range(n) if waiting[task] == 0]
	order = []
	while ready:
		task = max(ready)
		ready.remove(task)
		order.append(task)
		for other in unlocks[task]:
			waiting[other] -= 1
			if waiting[other] == 0:
				ready.append(other)
	return order if len(order) == n else []

def plan_ancestors(n, prereqs, task):
	found = []

	def climb(current):
		for later, needed in prereqs:
			if later == current and needed not in found:
				found.append(needed)
				climb(needed)

	climb(task)
	return sorted(found)
