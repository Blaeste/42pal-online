"""Reference solution of star_chart, for every variant: one function each."""

def chart_count(points, height, width):
	grid = []
	for row in range(height):
		line = ""
		for col in range(width):
			count = len([1 for point in points if point[0] == row and point[1] == col])
			if count == 0:
				line += "."
			elif count >= 10:
				line += "+"
			else:
				line += str(count)
		grid.append(line)
	return grid

def chart_bounds(points):
	if len(points) == 0:
		return []
	top = bottom = points[0][0]
	left = right = points[0][1]
	for row, col in points:
		top, bottom = min(top, row), max(bottom, row)
		left, right = min(left, col), max(right, col)
	grid = []
	for row in range(top, bottom + 1):
		grid.append("".join("*" if (row, col) in points else "." for col in range(left, right + 1)))
	return grid

def chart_up(points, size):
	grid = [["."] * size for _ in range(size)]
	for x, y in points:
		if 0 <= x < size and 0 <= y < size:
			grid[size - 1 - y][x] = "*"
	return ["".join(line) for line in grid]
