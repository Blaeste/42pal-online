"""Reference solution of string_pack, for every variant: one function each."""

def pack_escape(items):
	out = ""
	for item in items:
		for char in item:
			if char in "\\;":
				out += "\\"
			out += char
		out += ";"
	return out

def unpack_escape(packed):
	items = []
	current = ""
	escaped = False
	for char in packed:
		if escaped:
			if char not in "\\;":
				return None
			current += char
			escaped = False
		elif char == "\\":
			escaped = True
		elif char == ";":
			items.append(current)
			current = ""
		else:
			current += char
	if escaped or current:
		return None
	return items

def unpack_length(packed):
	items = []
	index = 0
	while index < len(packed):
		colon = packed.find(":", index)
		digits = packed[index:colon] if colon >= 0 else ""
		if digits == "" or not all("0" <= char <= "9" for char in digits):
			return None
		size = int(digits)
		start = colon + 1
		if start + size > len(packed):
			return None
		items.append(packed[start:start + size])
		index = start + size
	return items
