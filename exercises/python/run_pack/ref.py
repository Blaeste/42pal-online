"""Reference solution of run_pack, for every variant: one function each."""

def runs_pairs(text):
	found = []
	for char in text:
		if found and found[-1][0] == char:
			found[-1] = (char, found[-1][1] + 1)
		else:
			found.append((char, 1))
	return found

def runs_count_first(text):
	out = ""
	for char, size in runs_pairs(text):
		if size > 1:
			out += str(size)
		out += char
	return out

def runs_expand(packed):
	out = ""
	digits = ""
	for char in packed:
		if "0" <= char <= "9":
			digits += char
		else:
			out += char * (int(digits) if digits else 1)
			digits = ""
	return out
