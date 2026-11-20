"""Reference solution of word_chain, for every variant: one function each."""

def _changed(a, b):
	if len(a) != len(b):
		return False
	return len([1 for i in range(len(a)) if a[i] != b[i]]) == 1

def _edited(a, b):
	if _changed(a, b):
		return True
	if abs(len(a) - len(b)) != 1:
		return False
	longer, shorter = (a, b) if len(a) > len(b) else (b, a)
	i = 0
	while i < len(shorter) and longer[i] == shorter[i]:
		i += 1
	return longer[i + 1:] == shorter[i:]

def _levels(start, words, linked):
	"""Breadth-first, level by level: {word: the word before it}."""
	before = {start: None}
	level = [start]
	while level:
		following = []
		for word in level:
			for other in words:
				if other not in before and linked(word, other):
					before[other] = word
					following.append(other)
		level = following
	return before

def chain_path(start, end, words):
	if start == end:
		return [start]
	if end not in words:
		return None
	before = _levels(start, words, _changed)
	if end not in before:
		return None
	path = [end]
	while path[0] != start:
		path.insert(0, before[path[0]])
	return path

def chain_reachable(start, words):
	return len([word for word in _levels(start, words, _changed) if word != start])

def chain_grow(start, end, words):
	if start == end:
		return 1
	if end not in words:
		return 0
	before = _levels(start, words, _edited)
	if end not in before:
		return 0
	count = 1
	word = end
	while word != start:
		word = before[word]
		count += 1
	return count
