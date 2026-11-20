"""Reference solution of key_sort, for every variant: an insertion sort each."""

def _is_consonant(char):
	return ("a" <= char <= "z" or "A" <= char <= "Z") and char not in "aeiouAEIOU"

def _insertion(words, before):
	"""Sort a copy of words; before(x, y) tells whether x must come before y."""
	result = []
	for word in words:
		place = len(result)
		while place > 0 and before(word, result[place - 1]):
			place -= 1
		result.insert(place, word)
	return result

def _consonants_first(x, y):
	count_x = len([char for char in x if _is_consonant(char)])
	count_y = len([char for char in y if _is_consonant(char)])
	if count_x != count_y:
		return count_x < count_y
	return x.lower() < y.lower()

def _last_char_first(x, y):
	if x[-1:] != y[-1:]:
		return x[-1:] < y[-1:]
	return len(x) > len(y)

def _digits_first(x, y):
	digits_x = len([char for char in x if "0" <= char <= "9"])
	digits_y = len([char for char in y if "0" <= char <= "9"])
	if digits_x != digits_y:
		return digits_x > digits_y
	return len(x) < len(y)

def sort_by_consonants(words):
	return _insertion(words, _consonants_first)

def sort_by_last_char(words):
	return _insertion(words, _last_char_first)

def sort_by_digits(words):
	return _insertion(words, _digits_first)
