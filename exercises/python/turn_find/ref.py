"""Reference solution of turn_find, for every variant: one function each."""

def _gives(a, b, k):
	"""Does a turned k places to the right give b? (same lengths)"""
	size = len(a)
	for index in range(size):
		if a[(index - k) % size] != b[index]:
			return False
	return True

def _ks(a, b):
	if len(a) != len(b):
		return []
	if len(a) == 0:
		return [0]
	return [k for k in range(len(a)) if _gives(a, b, k)]

def turn_steps(a, b):
	found = _ks(a, b)
	if found:
		return found[0]
	return -1

def turn_all_steps(a, b):
	return _ks(a, b)

def turn_mirrored(a, b):
	return len(_ks(list(reversed(a)), b)) > 0
