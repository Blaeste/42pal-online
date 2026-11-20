"""Reference solution of case_wave, for every variant: one function each."""

def _letter(char):
	return "a" <= char <= "z" or "A" <= char <= "Z"

def _cased(char, upper):
	return char.upper() if upper else char.lower()

def wave_words(text):
	words = text.split(" ")
	result = []
	for word in words:
		count = 0
		out = ""
		for char in word:
			if _letter(char):
				out += _cased(char, count % 2 == 0)
				count += 1
			else:
				out += char
		result.append(out)
	return " ".join(result)

def wave_pattern(text, pattern):
	out = ""
	count = 0
	for char in text:
		if _letter(char):
			out += _cased(char, pattern[count % len(pattern)] == "u")
			count += 1
		else:
			out += char
	return out

def wave_all_chars(text):
	return "".join(_cased(char, index % 2 == 0) if _letter(char) else char
		for index, char in enumerate(text))
