"""Reference solution of word_complete, for every variant: one function each.

A prefix tree of dicts; "#" counts the words that end at a node, "+" the
words that go through it.
"""

def _tree(words):
	root = {"#": 0, "+": 0}
	for word in words:
		node = root
		node["+"] += 1
		for char in word:
			node = node.setdefault(char, {"#": 0, "+": 0})
			node["+"] += 1
		node["#"] += 1
	return root

def _down(node, text):
	for char in text:
		if char not in node:
			return None
		node = node[char]
	return node

def _words_below(node, start):
	"""(word, count) for each word under node, start being the text up to it."""
	found = []
	if node["#"]:
		found.append((start, node["#"]))
	for char, child in node.items():
		if char not in ("#", "+"):
			found += _words_below(child, start + char)
	return found

def complete_top_k(words, prefix, k):
	node = _down(_tree(words), prefix)
	if node is None:
		return []
	found = _words_below(node, prefix)
	ranked = []
	for word, count in found:
		place = 0
		while place < len(ranked) and (ranked[place][1] > count
				or (ranked[place][1] == count and ranked[place][0] < word)):
			place += 1
		ranked.insert(place, (word, count))
	return [word for word, _ in ranked[:k]]

def complete_next_letters(words, prefix):
	node = _down(_tree(words), prefix)
	if node is None:
		return ""
	letters = [char for char in node if char not in ("#", "+")]
	for i in range(len(letters)):
		for j in range(len(letters) - 1 - i):
			if letters[j] > letters[j + 1]:
				letters[j], letters[j + 1] = letters[j + 1], letters[j]
	return "".join(letters)

def complete_shortest_unique(words):
	root = _tree(words)
	result = []
	for word in words:
		node = root
		answer = word
		for size, char in enumerate(word, start=1):
			node = node[char]
			# Only this word goes through this node: the prefix tells it apart.
			if node["+"] == 1:
				answer = word[:size]
				break
		result.append(answer)
	return result
