"""Reference solution of merge_many, for every variant: one function each."""

def _merge(lists, better):
	"""Merge the lists; better(x, y) tells whether x is taken before y.

	Returns (values, origins): each value taken, and the index of its list.
	"""
	places = [0] * len(lists)
	taken, origins = [], []
	while True:
		best = -1
		for index in range(len(lists)):
			if places[index] < len(lists[index]):
				if best < 0 or better(lists[index][places[index]], lists[best][places[best]]):
					best = index
		if best < 0:
			return taken, origins
		taken.append(lists[best][places[best]])
		origins.append(best)
		places[best] += 1

def many_descending(lists):
	return _merge(lists, lambda x, y: x > y)[0]

def many_first_k(lists, k):
	return _merge(lists, lambda x, y: x < y)[0][:k]

def many_origins(lists):
	return _merge(lists, lambda x, y: x < y)[1]
