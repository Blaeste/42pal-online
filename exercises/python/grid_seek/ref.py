"""Reference solution of grid_seek, for every variant: one function each."""

STEPS = {"R": (0, 1), "D": (1, 0), "L": (0, -1), "U": (-1, 0),
	"DR": (1, 1), "DL": (1, -1), "UL": (-1, -1), "UR": (-1, 1)}

def _line(grid, row, col, dr, dc, size):
	"""The letters from (row, col) in the direction, size of them, or None past the edge."""
	letters = ""
	for _ in range(size):
		if row < 0 or col < 0 or row >= len(grid) or col >= len(grid[0]):
			return None
		letters += grid[row][col]
		row += dr
		col += dc
	return letters

def seek_first(grid, word):
	for row in range(len(grid)):
		for col in range(len(grid[0])):
			for name, (dr, dc) in STEPS.items():
				if _line(grid, row, col, dr, dc, len(word)) == word:
					return (row, col, name)
	return None

def seek_straight(grid, word):
	count = 0
	for row in range(len(grid)):
		for col in range(len(grid[0])):
			for name in ("R", "D", "L", "U"):
				dr, dc = STEPS[name]
				if _line(grid, row, col, dr, dc, len(word)) == word:
					count += 1
	return count

def seek_path(grid, word):
	def walk(row, col, index, used):
		if row < 0 or col < 0 or row >= len(grid) or col >= len(grid[0]):
			return False
		if (row, col) in used or grid[row][col] != word[index]:
			return False
		if index == len(word) - 1:
			return True
		used.add((row, col))
		for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
			if walk(row + dr, col + dc, index + 1, used):
				return True
		used.remove((row, col))
		return False

	return any(walk(row, col, 0, set()) for row in range(len(grid)) for col in range(len(grid[0])))
