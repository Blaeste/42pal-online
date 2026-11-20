"""board_threat: an original program model in the style of "is a piece
attacked on a board".

The board is given row by row as the arguments, with one target T and
pieces of our own: knights that jump, guards that attack the squares around
them, and lines that attack along their row and column up to the first
square that is not empty. The program counts the pieces that attack T, or
says where they are. No chess king, no chess board of fixed size, and no
Success or Fail: the real 42 subject is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

# The letters of the pieces of each variant; every other character is an empty square.
LETTERS = {"knights": "N", "guards": "G", "lines": "L", "mixed": "NGL"}

KNIGHT_JUMPS = {(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)}
DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))

def attacks(rows, row, col, target, letters):
	"""Does the piece at (row, col) attack the target?"""
	piece = rows[row][col]
	gap = (target[0] - row, target[1] - col)
	if piece == "N":
		return gap in KNIGHT_JUMPS
	if piece == "G":
		return abs(gap[0]) <= 1 and abs(gap[1]) <= 1
	for step_row, step_col in DIRECTIONS:
		r, c = row + step_row, col + step_col
		while 0 <= r < len(rows) and 0 <= c < len(rows[0]):
			if rows[r][c] == "T":
				return True
			if rows[r][c] in letters:
				break
			r, c = r + step_row, c + step_col
	return False

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	rows = test.args
	if not rows:
		return "\n"
	letters = LETTERS[params["pieces"]]
	target = next((r, c) for r, line in enumerate(rows) for c, char in enumerate(line) if char == "T")
	found = [(r, c) for r, line in enumerate(rows) for c, char in enumerate(line)
		if char in letters and attacks(rows, r, c, target, letters)]
	if params["answer"] == "count":
		return f"{len(found)}\n"
	if not found:
		return "safe\n"
	return "".join(f"{r + 1},{c + 1}\n" for r, c in found)

def random_board(rng):
	"""A board of 1 to 6 rows of 1 to 7 squares, with one T and pieces of every kind."""
	height, width = rng.randint(1, 6), rng.randint(1, 7)
	cells = [[rng.choice("....NGLx") for _ in range(width)] for _ in range(height)]
	cells[rng.randrange(height)][rng.randrange(width)] = "T"
	return tuple("".join(row) for row in cells)

def generate_tests(params, rng):
	"""Return the test cases: fixed boards first, then random ones."""
	tests = [
		TestCase(()),
		TestCase(("T",)),
		TestCase(("N....", "..T..", "....N", ".N...")),
		TestCase(("G..", ".T.", "..G", "G..")),
		TestCase(("L.T.L", ".....", "..L..", "..L..")),
		TestCase(("N.L..", "..T.G", "G...L", "..L.N")),
		TestCase(("LLTLL",)),
		TestCase(("L", ".", "N", "T")),
	]
	for _ in range(12):
		tests.append(TestCase(random_board(rng)))
	return tests

KNIGHT = ("the squares two rows and one column away from it, or two columns and one\n"
	"row away; it jumps over the squares in between")
GUARD = "the 8 squares around it"
LINE = ("the squares of its row and of its column, in the 4 directions, up to the\n"
	"first square that is not empty (a piece or T), which is attacked too")

EXERCISE = Exercise(
	name="board_threat",
	language="c",
	kind="program",
	assignment_name="threat_${answer}_${pieces}",
	expected_files=("threat_${answer}_${pieces}.c",),
	allowed_functions=("write",),
	themes=("grid_attack",),
	params=(
		Param("answer", ("count", "where"), {
			"count": "the number of pieces that attack T, followed by a newline",
			"where": "the position of each piece that attacks T, as row,column followed by a\n"
				"newline, in the order of the board: row by row from the first one, each\n"
				"row from left to right. If no piece attacks T, it displays safe followed\n"
				"by a newline",
		}),
		Param("pieces", ("knights", "guards", "lines", "mixed"), {
			"knights": f"The pieces are the N. An N attacks {KNIGHT}.",
			"guards": f"The pieces are the G. A G attacks {GUARD}.",
			"lines": f"The pieces are the L. An L attacks {LINE}.",
			"mixed": f"The pieces are the N, the G and the L:\n- an N attacks {KNIGHT};\n"
				f"- a G attacks {GUARD};\n- an L attacks {LINE}.",
		}),
	),
	subject=(
		"Write a program that takes a board, given row by row as its arguments, and\n"
		"displays\n"
		"$answer.\n"
		"\n"
		"The arguments all have the same length. The board holds exactly one T, the\n"
		"target; every character that is neither T nor a piece is an empty square.\n"
		"\n"
		"$pieces\n"
		"\n"
		"The rows are numbered from 1 (the first argument is row 1), and the columns\n"
		"from 1, from the left.\n"
		"\n"
		"If there is no argument, the program displays a newline."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	examples=(
		TestCase(("N.L..", "..T.G", "G...L", "..L.N")),
		TestCase(("L.T.L", ".....", "..L..", "..L..")),
		TestCase(()),
	),
)
