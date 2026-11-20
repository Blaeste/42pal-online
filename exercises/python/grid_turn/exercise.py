"""grid_turn: an original Python model in the style of "build a matrix
flipped from another".

The student writes a function that returns a new matrix: upside down,
transposed, or turned a quarter to the right or to the left. Each row
reversed, the real subject, is not one of the moves.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def turned(matrix, move):
	columns = [list(column) for column in zip(*matrix)]
	if move == "upside_down":
		return [list(row) for row in matrix[::-1]]
	if move == "transpose":
		return columns
	if move == "rotate_right":
		return [column[::-1] for column in columns]
	return columns[::-1]

def oracle(params, test):
	(matrix,) = values(test)
	return shown(turned(matrix, params["move"]))

def generate_tests(params, rng):
	matrices = [[], [[7]], [[1, 2, 3], [4, 5, 6]], [[1], [2], [3]], [[1, 2], [3, 4]], [[0, -1, 5, 9]]]
	for _ in range(10):
		width = rng.randint(1, 4)
		matrices.append([[rng.randint(-9, 99) for _ in range(width)] for _ in range(rng.randint(1, 4))])
	return [case(matrix) for matrix in matrices]

EXERCISE = Exercise(
	name="grid_turn",
	language="python",
	kind="function",
	assignment_name="grid_${move}",
	expected_files=("grid_${move}.py",),
	allowed_functions=(),
	themes=("matrix_flip",),
	params=(
		Param("move", ("upside_down", "transpose", "rotate_right", "rotate_left"), {
			"upside_down": "upside down: its last row first, up to its first row last",
			"transpose": "transposed: its first row is the first column of the given matrix,\n"
				"its second row the second column, and so on",
			"rotate_right": "turned a quarter of a turn to the right (clockwise): its first row is\n"
				"the first column of the given matrix read from the bottom up",
			"rotate_left": "turned a quarter of a turn to the left (counterclockwise): its first\n"
				"row is the last column of the given matrix read from the top down",
		}),
	),
	subject=(
		"Write a function that takes a matrix (a list of rows, each a list of ints,\n"
		"all of the same length) and returns a new matrix: the given one\n"
		"$move.\n"
		"\n"
		"The given matrix must not be changed. An empty matrix gives an empty\n"
		"matrix; no row of a matrix is empty.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(matrix: list[list[int]]) -> list[list[int]]:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("grid_${move}"),
	call=call,
	examples=(case([[1, 2, 3], [4, 5, 6]]), case([[7]]), case([])),
)
