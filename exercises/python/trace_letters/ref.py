"""Reference solution of trace_letters, for every variant: one function each."""

def trace_positions(small, big):
	found = []
	start = 0
	for char in small:
		index = big.find(char, start)
		if index < 0:
			return None
		found.append(index)
		start = index + 1
	return found

def trace_count(small, big):
	if not small:
		return 0
	count = 0
	wanted = 0
	for char in big:
		if char == small[wanted]:
			wanted += 1
		if wanted == len(small):
			count += 1
			wanted = 0
	return count

def trace_nocase(small, big):
	return trace_positions(small.lower(), big.lower()) is not None
