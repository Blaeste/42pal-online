"""Reference solution of nest_check, for every variant: one function each."""

TWO = {")": "(", "]": "["}
FOUR = {")": "(", "]": "[", "}": "{", ">": "<"}

def _walk(text, pairs):
	"""Return (opened, count, deepest), or None when a closing bracket is wrong."""
	opened = []
	count = 0
	deepest = -1
	most = 0
	for index, char in enumerate(text):
		if char in pairs.values():
			opened.append(char)
			if len(opened) > most:
				most = len(opened)
				deepest = index
		elif char in pairs:
			if not opened or opened.pop() != pairs[char]:
				return None
			count += 1
	return opened, count, deepest

def _pairs(text, pairs):
	walk = _walk(text, pairs)
	if walk is None or walk[0]:
		return -1
	return walk[1]

def _deepest(text, pairs):
	walk = _walk(text, pairs)
	if walk is None or walk[0]:
		return -1
	return walk[2]

def _repair(text, pairs):
	walk = _walk(text, pairs)
	if walk is None:
		return None
	closing = {opener: closer for closer, opener in pairs.items()}
	end = ""
	for opener in walk[0]:
		end = closing[opener] + end
	return text + end

def nest_pairs_two(text):
	return _pairs(text, TWO)

def nest_pairs_four(text):
	return _pairs(text, FOUR)

def nest_deepest_two(text):
	return _deepest(text, TWO)

def nest_deepest_four(text):
	return _deepest(text, FOUR)

def nest_repair_two(text):
	return _repair(text, TWO)

def nest_repair_four(text):
	return _repair(text, FOUR)
