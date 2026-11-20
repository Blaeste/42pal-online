"""Reference solution of mirror_parts, for every variant: one function each.

A table first: mirror[i][j] tells whether text[i:j] reads the same both ways.
Then the answers for each end of the string, from the last position back.
"""

def _mirrors(text):
	size = len(text)
	mirror = [[False] * (size + 1) for _ in range(size + 1)]
	for start in range(size, -1, -1):
		for end in range(start, size + 1):
			length = end - start
			if length <= 1:
				mirror[start][end] = True
			else:
				mirror[start][end] = text[start] == text[end - 1] and mirror[start + 1][end - 1]
	return mirror

def parts_ways(text):
	size = len(text)
	mirror = _mirrors(text)
	ways = [0] * (size + 1)
	ways[size] = 1
	for start in range(size - 1, -1, -1):
		ways[start] = sum(ways[end] for end in range(start + 1, size + 1) if mirror[start][end])
	return ways[0]

def _best(text, shortest):
	"""best[i]: the best cut of text[i:], a list of parts, or None."""
	size = len(text)
	mirror = _mirrors(text)
	best = [None] * (size + 1)
	best[size] = []
	for start in range(size - 1, -1, -1):
		for end in range(size, start + shortest - 1, -1):
			if mirror[start][end] and best[end] is not None:
				if best[start] is None or len(best[end]) + 1 < len(best[start]):
					best[start] = [text[start:end]] + best[end]
	return best[0]

def parts_fewest(text):
	return _best(text, 1)

def parts_no_single(text):
	cut = _best(text, 2)
	return -1 if cut is None else len(cut)
