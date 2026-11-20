"""Reference solution of char_balance, for every variant: one function each."""

def _count(text):
	counts = {}
	for char in text:
		counts[char] = counts.get(char, 0) + 1
	return counts

def balance_changes(s1, s2):
	if len(s1) != len(s2):
		return -1
	counts = _count(s2)
	changes = 0
	for char in s1:
		if counts.get(char, 0) > 0:
			counts[char] -= 1
		else:
			changes += 1
	return changes

def balance_first_extra(s1, s2):
	in_s1, in_s2 = _count(s1), _count(s2)
	for char in s1:
		if in_s1[char] > in_s2.get(char, 0):
			return char
	return ""

def balance_window(small, big):
	size = len(small)
	wanted = _count(small)
	for start in range(len(big) - size + 1):
		if _count(big[start:start + size]) == wanted:
			return start
	return -1
