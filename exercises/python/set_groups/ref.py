"""Reference solution of set_groups: the Groups of every variant.

Each file of a variant holds this whole class; each variant only calls its
own methods. A parent for each element; the union hangs the smaller group
under the larger one. No path compression, so that undo can put a parent
back as it was.
"""

class Groups:
	def __init__(self, n=0):
		self.parent = {element: element for element in range(n)}
		self.sizes = {element: 1 for element in range(n)}
		self.groups = n
		self.done = []

	def _add(self, element):
		if element not in self.parent:
			self.parent[element] = element
			self.sizes[element] = 1
			self.groups += 1

	def _leader(self, element):
		self._add(element)
		while self.parent[element] != element:
			element = self.parent[element]
		return element

	def union(self, a, b):
		la, lb = self._leader(a), self._leader(b)
		if la == lb:
			return False
		if self.sizes[la] < self.sizes[lb]:
			la, lb = lb, la
		self.parent[lb] = la
		self.sizes[la] += self.sizes[lb]
		self.groups -= 1
		self.done.append((la, lb))
		return True

	def size(self, x):
		return self.sizes[self._leader(x)]

	def count(self):
		return self.groups

	def join(self, a, b):
		return self.union(a, b)

	def together(self, a, b):
		return self._leader(a) == self._leader(b)

	def same(self, a, b):
		return self.together(a, b)

	def members(self, a):
		leader = self._leader(a)
		return sorted(element for element in self.parent if self._leader(element) == leader)

	def undo(self):
		if not self.done:
			return False
		la, lb = self.done.pop()
		self.parent[lb] = lb
		self.sizes[la] -= self.sizes[lb]
		self.groups += 1
		return True
