"""Reference solution of zone_count, for every variant: one function each.

A recursive fill marks each region; the marks are kept in a set. The maps
of the tests are small: the recursion stays shallow.
"""

def _fill(grid, row, col, kind, marked, corners):
	"""Mark the region of kind around (row, col); return its cells."""
	if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
		return []
	if grid[row][col] != kind or (row, col) in marked:
		return []
	marked.add((row, col))
	cells = [(row, col)]
	for dr in (-1, 0, 1):
		for dc in (-1, 0, 1):
			if (dr, dc) != (0, 0) and (corners or dr == 0 or dc == 0):
				cells += _fill(grid, row + dr, col + dc, kind, marked, corners)
	return cells

def _regions(grid, kind, corners):
	marked = set()
	found = []
	for row in range(len(grid)):
		for col in range(len(grid[0])):
			cells = _fill(grid, row, col, kind, marked, corners)
			if cells:
				found.append(cells)
	return found

def zone_largest(grid):
	sizes = [len(cells) for cells in _regions(grid, "#", False)]
	return max(sizes) if sizes else 0

def zone_diagonal(grid):
	return len(_regions(grid, "#", True))

def zone_lakes(grid):
	count = 0
	for cells in _regions(grid, ".", False):
		if all(0 < row < len(grid) - 1 and 0 < col < len(grid[0]) - 1 for row, col in cells):
			count += 1
	return count

def zone_perimeter(grid):
	coast = 0
	for row in range(len(grid)):
		for col in range(len(grid[0])):
			if grid[row][col] != "#":
				continue
			for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
				r, c = row + dr, col + dc
				if r < 0 or c < 0 or r >= len(grid) or c >= len(grid[0]) or grid[r][c] == ".":
					coast += 1
	return coast
