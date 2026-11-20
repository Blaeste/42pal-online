"""Reference solution of top_heap: the Heap of every variant.

The rule is read from the name of the file (heap_max_heap.py,
heap_k_largest.py, heap_median.py), which the test main imports. The heaps
are lists sifted by hand; before(a, b) tells which value goes nearer the
top.
"""

RULE = __name__.split("_", 1)[-1]

def _push(items, value, before):
	items.append(value)
	child = len(items) - 1
	while child > 0:
		parent = (child - 1) // 2
		if not before(items[child], items[parent]):
			break
		items[child], items[parent] = items[parent], items[child]
		child = parent

def _pop(items, before):
	top = items[0]
	last = items.pop()
	if items:
		items[0] = last
		index = 0
		while True:
			best = index
			for child in (2 * index + 1, 2 * index + 2):
				if child < len(items) and before(items[child], items[best]):
					best = child
			if best == index:
				break
			items[index], items[best] = items[best], items[index]
			index = best
	return top

def _larger(a, b):
	return a > b

def _smaller(a, b):
	return a < b

class Heap:
	def __init__(self, k=0):
		self.k = k
		self.items = []
		self.low = []
		self.high = []

	def push(self, value):
		_push(self.items, value, _larger)

	def pop(self):
		return _pop(self.items, _larger) if self.items else None

	def peek(self):
		return self.items[0] if self.items else None

	def size(self):
		return len(self.items)

	def add(self, value):
		if RULE == "k_largest":
			_push(self.items, value, _smaller)
			if len(self.items) > self.k:
				_pop(self.items, _smaller)
			return
		# median: low holds the smaller half (largest on top), high the larger half.
		if self.low and value > self.low[0]:
			_push(self.high, value, _smaller)
		else:
			_push(self.low, value, _larger)
		if len(self.low) > len(self.high) + 1:
			_push(self.high, _pop(self.low, _larger), _smaller)
		elif len(self.high) > len(self.low):
			_push(self.low, _pop(self.high, _smaller), _larger)

	def kth(self):
		return self.items[0] if len(self.items) == self.k else None

	def median(self):
		return self.low[0] if self.low else None
