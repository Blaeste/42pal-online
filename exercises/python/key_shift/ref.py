"""Reference solution of key_shift, for every variant: one function each."""

LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = LOWER.upper()

def _shift(char, shift):
	if char in LOWER:
		return LOWER[(LOWER.index(char) + shift) % 26]
	if char in UPPER:
		return UPPER[(UPPER.index(char) + shift) % 26]
	return char

def shift_by_key(text, key):
	out = []
	used = 0
	for char in text:
		if char in LOWER or char in UPPER:
			out.append(_shift(char, LOWER.index(key[used % len(key)].lower())))
			used += 1
		else:
			out.append(char)
	return "".join(out)

def shift_growing(text, step):
	out = []
	count = 0
	for char in text:
		if char in LOWER or char in UPPER:
			out.append(_shift(char, count * step))
			count += 1
		else:
			out.append(char)
	return "".join(out)

def shift_with_digits(text, shift):
	out = []
	for char in text:
		if "0" <= char <= "9":
			out.append(str((int(char) + shift) % 10))
		else:
			out.append(_shift(char, shift))
	return "".join(out)
