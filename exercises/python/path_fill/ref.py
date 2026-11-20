"""Reference solution of path_fill, for every variant: one function each.

The spirals go layer by layer, with the bounds of the layer left to fill.
"""

def fill_rect_spiral(rows, cols):
	if rows == 0 or cols == 0:
		return []
	grid = [[0] * cols for _ in range(rows)]
	top, bottom, left, right = 0, rows - 1, 0, cols - 1
	number = 1
	while top <= bottom and left <= right:
		for col in range(left, right + 1):
			grid[top][col] = number
			number += 1
		for row in range(top + 1, bottom + 1):
			grid[row][right] = number
			number += 1
		if top < bottom:
			for col in range(right - 1, left - 1, -1):
				grid[bottom][col] = number
				number += 1
		if left < right:
			for row in range(bottom - 1, top, -1):
				grid[row][left] = number
				number += 1
		top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1
	return grid

def fill_counter(n):
	# The counterclockwise spiral is the clockwise one of the transposed matrix.
	grid = fill_rect_spiral(n, n)
	return [[grid[col][row] for col in range(n)] for row in range(n)]

def fill_snake(rows, cols):
	if rows == 0 or cols == 0:
		return []
	grid = []
	for row in range(rows):
		line = [row * cols + col + 1 for col in range(cols)]
		if row % 2 == 1:
			line.reverse()
		grid.append(line)
	return grid
