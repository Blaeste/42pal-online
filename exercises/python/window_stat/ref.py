"""Reference solution of window_stat, for every variant: one function each.

min and spread keep a deque of indexes, like the classic window maximum;
distinct keeps the counts of the window; first_negative the negative ones.
"""

def _windows_ok(nums, k):
	return 1 <= k <= len(nums)

def _extreme(nums, k, keep):
	"""The value of each window that wins `keep` against all the others."""
	if not _windows_ok(nums, k):
		return []
	order = []
	result = []
	for index, value in enumerate(nums):
		while order and not keep(nums[order[-1]], value):
			order.pop()
		order.append(index)
		if order[0] <= index - k:
			order.pop(0)
		if index >= k - 1:
			result.append(nums[order[0]])
	return result

def window_min(nums, k):
	return _extreme(nums, k, lambda old, new: old < new)

def window_spread(nums, k):
	smallest = _extreme(nums, k, lambda old, new: old < new)
	largest = _extreme(nums, k, lambda old, new: old > new)
	return [high - low for high, low in zip(largest, smallest)]

def window_distinct(nums, k):
	if not _windows_ok(nums, k):
		return []
	counts = {}
	result = []
	for index, value in enumerate(nums):
		counts[value] = counts.get(value, 0) + 1
		if index >= k:
			old = nums[index - k]
			counts[old] -= 1
			if counts[old] == 0:
				del counts[old]
		if index >= k - 1:
			result.append(len(counts))
	return result

def window_first_negative(nums, k):
	if not _windows_ok(nums, k):
		return []
	negatives = [index for index, value in enumerate(nums) if value < 0]
	result = []
	for start in range(len(nums) - k + 1):
		inside = [index for index in negatives if start <= index < start + k]
		result.append(nums[inside[0]] if inside else 0)
	return result
