"""Reference solution of word_tree: the WordTree of every variant.

Each file of a variant holds this whole class; each variant only calls its
own methods. A node is a dict of the letters that follow, with two counts:
"#" the words that end here, "+" the words that go through here.
"""

class WordTree:
	def __init__(self):
		self.root = {"#": 0, "+": 0}

	def add(self, word):
		node = self.root
		node["+"] += 1
		for letter in word:
			node = node.setdefault(letter, {"#": 0, "+": 0})
			node["+"] += 1
		node["#"] += 1

	def _node(self, text):
		node = self.root
		for letter in text:
			if letter not in node:
				return None
			node = node[letter]
		return node

	def count(self, prefix):
		node = self._node(prefix)
		return node["+"] if node else 0

	def remove(self, word):
		node = self._node(word)
		if node is None or node["#"] == 0:
			return False
		node = self.root
		node["+"] -= 1
		for letter in word:
			node = node[letter]
			node["+"] -= 1
		node["#"] -= 1
		return True

	def longest(self, text):
		best = ""
		node = self.root
		for index, letter in enumerate(text):
			if node["#"] > 0:
				best = text[:index]
			if letter not in node:
				return best
			node = node[letter]
		return text if node["#"] > 0 else best

	def match(self, pattern):
		def walk(node, index):
			if index == len(pattern):
				return node["#"] > 0
			letters = [key for key in node if key not in "#+"] if pattern[index] == "." else [pattern[index]]
			return any(letter in node and walk(node[letter], index + 1) for letter in letters)

		return walk(self.root, 0)
