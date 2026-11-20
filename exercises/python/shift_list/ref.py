"""Reference solution of shift_list, for every variant: one function each."""

def shift_left(items, k):
	size = len(items)
	return [items[(index + k) % size] for index in range(size)]

def shift_blocks(items, k):
	result = []
	start = 0
	while start < len(items):
		end = min(start + k, len(items))
		for index in range(end - 1, start - 1, -1):
			result.append(items[index])
		start = end
	return result

def shift_keep_negatives(items, k):
	places = [index for index in range(len(items)) if items[index] >= 0]
	size = len(places)
	result = items[:]
	for position, place in enumerate(places):
		result[place] = items[places[(position - k) % size]]
	return result
