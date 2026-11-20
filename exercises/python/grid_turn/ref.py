"""Reference solution of grid_turn, for every variant: one function each."""

def _size(matrix):
	return len(matrix), len(matrix[0]) if matrix else 0

def grid_upside_down(matrix):
	rows, _ = _size(matrix)
	return [matrix[rows - 1 - row][:] for row in range(rows)]

def grid_transpose(matrix):
	rows, cols = _size(matrix)
	return [[matrix[row][col] for row in range(rows)] for col in range(cols)]

def grid_rotate_right(matrix):
	rows, cols = _size(matrix)
	return [[matrix[rows - 1 - row][col] for row in range(rows)] for col in range(cols)]

def grid_rotate_left(matrix):
	rows, cols = _size(matrix)
	return [[matrix[row][cols - 1 - col] for row in range(rows)] for col in range(cols)]
