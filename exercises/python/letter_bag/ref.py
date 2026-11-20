"""Reference solution of letter_bag, for every variant: one function each."""

def _counts(text):
	"""26 counts, one for each letter from a to z."""
	counts = [0] * 26
	for char in text.lower():
		if "a" <= char <= "z":
			counts[ord(char) - ord("a")] += 1
	return counts

def bag_missing(have, want):
	have_counts, want_counts = _counts(have), _counts(want)
	result = ""
	for index in range(26):
		if want_counts[index] > have_counts[index]:
			result += chr(ord("a") + index) * (want_counts[index] - have_counts[index])
	return result

def bag_groups(words):
	keys = []
	groups = []
	for word in words:
		key = _counts(word)
		if key in keys:
			groups[keys.index(key)].append(word)
		else:
			keys.append(key)
			groups.append([word])
	return groups

def bag_can_write(word, text):
	needed, given = _counts(word), _counts(text)
	return all(needed[index] <= given[index] for index in range(26))
