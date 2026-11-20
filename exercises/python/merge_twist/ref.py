"""Reference solution of merge_twist, for every variant: one function each."""

def merge_descending(a, b):
	result = []
	i = j = 0
	while i < len(a) and j < len(b):
		if a[i] >= b[j]:
			result.append(a[i])
			i += 1
		else:
			result.append(b[j])
			j += 1
	return result + a[i:] + b[j:]

def merge_unique(a, b):
	result = []
	i = j = 0
	while i < len(a) or j < len(b):
		if j >= len(b) or (i < len(a) and a[i] <= b[j]):
			value = a[i]
			i += 1
		else:
			value = b[j]
			j += 1
		if not result or result[-1] != value:
			result.append(value)
	return result

def merge_path(a, b):
	letters = []
	i = j = 0
	while i < len(a) and j < len(b):
		if a[i] <= b[j]:
			letters.append("a")
			i += 1
		else:
			letters.append("b")
			j += 1
	return "".join(letters) + "a" * (len(a) - i) + "b" * (len(b) - j)
