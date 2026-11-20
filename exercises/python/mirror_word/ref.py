"""Reference solution of mirror_word, for every variant: one function each."""

def _same_both_ways(chars, start, end):
	"""Do chars[start..end] (end included) read the same from both ends?"""
	while start < end:
		if chars[start] != chars[end]:
			return False
		start += 1
		end -= 1
	return True

def mirror_digits(text):
	digits = [char for char in text if "0" <= char <= "9"]
	return _same_both_ways(digits, 0, len(digits) - 1)

def mirror_longest_word(text):
	best = ""
	for word in text.split(" "):
		lower = word.lower()
		if len(word) > len(best) and _same_both_ways(lower, 0, len(lower) - 1):
			best = word
	return best

def mirror_near(text):
	letters = [char.lower() for char in text if char.isalpha()]
	start, end = 0, len(letters) - 1
	while start < end and letters[start] == letters[end]:
		start += 1
		end -= 1
	if start >= end:
		return True
	# The first two letters that differ: one of them must go.
	return (_same_both_ways(letters, start + 1, end)
		or _same_both_ways(letters, start, end - 1))
