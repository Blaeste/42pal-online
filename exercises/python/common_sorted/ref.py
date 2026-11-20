"""Reference solution of common_sorted, for every variant: one function each."""

def _list_counts(lists):
	"""For each value, in how many lists it is: a dict."""
	counts = {}
	for numbers in lists:
		for value in set(numbers):
			counts[value] = counts.get(value, 0) + 1
	return counts

def _ascending(numbers):
	result = list(numbers)
	for i in range(1, len(result)):
		j = i
		while j > 0 and result[j - 1] > result[j]:
			result[j - 1], result[j] = result[j], result[j - 1]
			j -= 1
	return result

def common_at_least(lists, m):
	return _ascending(value for value, count in _list_counts(lists).items() if count >= m)

def common_only_one(lists):
	return _ascending(value for value, count in _list_counts(lists).items() if count == 1)

def common_with_counts(lists):
	if not lists:
		return []
	result = []
	positions = [0] * len(lists)
	# Walk all the lists together, like a merge: a value is kept when every
	# list has it at its current position.
	while all(positions[i] < len(lists[i]) for i in range(len(lists))):
		heads = [lists[i][positions[i]] for i in range(len(lists))]
		smallest = min(heads)
		if all(head == smallest for head in heads):
			result.append(smallest)
			positions = [p + 1 for p in positions]
		else:
			for i in range(len(lists)):
				if heads[i] == smallest:
					positions[i] += 1
	return result
