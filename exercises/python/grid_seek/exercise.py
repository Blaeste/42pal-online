"""grid_seek: an original Python model in the style of "find words in a grid
in every direction".

The student writes a function that looks for a word in a grid of letters:
its first place in a straight line, whether it can be spelled by a path of
neighbouring cells, or how many times it is written straight in four
directions. Every place in the 8 directions with their codes, the real
subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

DIRECTIONS = [("R", 0, 1), ("D", 1, 0), ("L", 0, -1), ("U", -1, 0),
	("DR", 1, 1), ("DL", 1, -1), ("UL", -1, -1), ("UR", -1, 1)]

def written(grid, word, row, col, dr, dc):
	for index, char in enumerate(word):
		r, c = row + index * dr, col + index * dc
		if not (0 <= r < len(grid) and 0 <= c < len(grid[r])) or grid[r][c] != char:
			return False
	return True

def spelled(grid, word, row, col, used):
	if grid[row][col] != word[0]:
		return False
	if len(word) == 1:
		return True
	used = used | {(row, col)}
	for _, dr, dc in DIRECTIONS[:4]:
		r, c = row + dr, col + dc
		if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and (r, c) not in used \
				and spelled(grid, word[1:], r, c, used):
			return True
	return False

def oracle(params, test):
	grid, word = values(test)
	cells = [(row, col) for row in range(len(grid)) for col in range(len(grid[0]) if grid else 0)]
	rule = params["rule"]
	if rule == "first":
		return shown(next(((row, col, name) for row, col in cells for name, dr, dc in DIRECTIONS
			if written(grid, word, row, col, dr, dc)), None))
	if rule == "straight":
		return shown(sum(1 for row, col in cells for _, dr, dc in DIRECTIONS[:4]
			if written(grid, word, row, col, dr, dc)))
	return shown(any(spelled(grid, word, row, col, set()) for row, col in cells))

def generate_tests(params, rng):
	pairs = [(["cat", "aox", "tac"], "cat"), (["cat", "aox", "tac"], "tac"), (["cat", "aox", "tac"], "xyz"),
		(["cat", "aox", "tac"], "cao"), (["cat", "aox", "tac"], "cac"), (["abc", "def", "ghi"], "aei"),
		(["abc", "def", "ghi"], "fed"), (["aa", "aa"], "aaa"), (["ab", "cd"], "abdc"), (["xyz"], "zy")]
	for _ in range(10):
		width = rng.randint(2, 5)
		grid = ["".join(rng.choice("abo") for _ in range(width)) for _ in range(rng.randint(2, 5))]
		pairs.append((grid, "".join(rng.choice("abo") for _ in range(rng.randint(2, 4)))))
	return [case(grid, word) for grid, word in pairs]

RULES = {
	"first": ("tuple[int, int, str] | None", "The function returns the first place where the\n"
		"word is written in a straight line, as a (row, col, direction) tuple: row\n"
		"and col are those of its first letter, and direction is the way it goes,\n"
		"one of these 8, in this order:\n"
		"- R (right), D (down), L (left), U (up),\n"
		"- DR (down-right), DL (down-left), UL (up-left), UR (up-right).\n"
		"\n"
		"The places are tried cell by cell, row by row from the top and each row\n"
		"from the left; for each cell, the 8 directions in the order above. If the\n"
		"word is nowhere, the function returns None."),
	"path": ("bool", "The function returns True if the word can be spelled along a path of\n"
		"cells: its first letter in a cell, then each next letter in a cell next\n"
		"to the one before by a side (up, down, left or right), no cell used\n"
		"twice. Otherwise it returns False."),
	"straight": ("int", "The function returns how many times the word is written in a\n"
		"straight line, going right, down, left or up. A first cell and a\n"
		"direction count once each: a word that reads the same both ways, written\n"
		"once in the grid, counts twice."),
}

EXERCISE = Exercise(
	name="grid_seek",
	language="python",
	kind="function",
	assignment_name="seek_${rule}",
	expected_files=("seek_${rule}.py",),
	allowed_functions=(),
	themes=("grid_word_search",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a grid of letters and a word of 2 letters or\n"
		"more. The grid is a list of strings of the same length: row 0 is the first\n"
		"string, and column 0 the first character of each string.\n"
		"\n"
		"$rule\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("seek_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}(grid: list[str], word: str) -> {RULES[params['rule']][0]}:",
	examples=lambda params: {
		"first": (case(["cat", "aox", "tac"], "tac"), case(["cat", "aox", "tac"], "xyz")),
		"path": (case(["cat", "aox", "tac"], "cao"), case(["cat", "aox", "tac"], "cac")),
		"straight": (case(["cat", "aox", "tac"], "cat"),),
	}[params["rule"]],
)
