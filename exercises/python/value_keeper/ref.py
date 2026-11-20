"""Reference solution of value_keeper: the Keeper of every variant.

The rule is read from the name of the file (keeper_lfu.py, keeper_fifo.py,
keeper_mru.py), which the test main imports: one class for the three. A
list keeps the keys in order of their last use (or of their coming in).
"""

RULE = __name__.rsplit("_", 1)[-1]

class Keeper:
	def __init__(self, capacity):
		self.capacity = capacity
		self.values = {}
		self.uses = {}
		self.order = []

	def _touch(self, key):
		self.uses[key] = self.uses.get(key, 0) + 1
		if RULE != "fifo":
			if key in self.order:
				self.order.remove(key)
			self.order.append(key)

	def get(self, key):
		if key not in self.values:
			return -1
		self._touch(key)
		return self.values[key]

	def put(self, key, value):
		if key not in self.values:
			if len(self.values) == self.capacity:
				if RULE == "lfu":
					fewest = min(self.uses[k] for k in self.order)
					out = [k for k in self.order if self.uses[k] == fewest][0]
				elif RULE == "fifo":
					out = self.order[0]
				else:
					out = self.order[-1]
				self.order.remove(out)
				del self.values[out]
				del self.uses[out]
			if RULE == "fifo":
				self.order.append(key)
		self.values[key] = value
		self._touch(key)
