"""Reference solution of char_mix, for every variant: one function each."""

def _without(source, other):
	result = ""
	for char in source:
		if char not in other and char not in result:
			result += char
	return result

def mix_only_first(s1, s2):
	return _without(s1, s2)

def mix_one_side(s1, s2):
	return _without(s1, s2) + _without(s2, s1)

def mix_common_count(s1, s2):
	counts = {}
	for char in s1:
		if char in s2 and char not in counts:
			in_s1 = len([c for c in s1 if c == char])
			in_s2 = len([c for c in s2 if c == char])
			counts[char] = in_s1 if in_s1 < in_s2 else in_s2
	return counts
