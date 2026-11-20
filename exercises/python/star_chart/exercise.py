"""star_chart: an original Python model in the style of "draw points on a
grid of characters".

The student writes a function that draws points as a list of strings: how
many points fall on each cell, the smallest rectangle around them, or a
grid where y goes up like on a graph. A square grid of * with (row, col)
points, the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def oracle(params, test):
	rule = params["rule"]
	if rule == "count":
		points, height, width = values(test)
		cells = [[0] * width for _ in range(height)]
		for row, col in points:
			if 0 <= row < height and 0 <= col < width:
				cells[row][col] += 1
		return shown(["".join("." if n == 0 else str(n) if n < 10 else "+" for n in line) for line in cells])
	if rule == "bounds":
		(points,) = values(test)
		if not points:
			return shown([])
		rows = range(min(p[0] for p in points), max(p[0] for p in points) + 1)
		cols = range(min(p[1] for p in points), max(p[1] for p in points) + 1)
		marked = set(points)
		return shown(["".join("*" if (row, col) in marked else "." for col in cols) for row in rows])
	points, size = values(test)
	marked = set(points)
	return shown(["".join("*" if (x, size - 1 - line) in marked else "." for x in range(size))
		for line in range(size)])

def random_points(rng, low, high):
	return [(rng.randint(low, high), rng.randint(low, high)) for _ in range(rng.randint(0, 7))]

def generate_tests(params, rng):
	rule = params["rule"]
	if rule == "count":
		tests = [case([(0, 0), (0, 0), (1, 2), (5, 5)], 2, 3), case([], 2, 2), case([(0, 0)] * 12, 1, 1),
			case([(1, 0), (-1, 0)], 3, 1)]
		tests += [case(random_points(rng, -1, 4), rng.randint(1, 4), rng.randint(1, 5)) for _ in range(10)]
	elif rule == "bounds":
		tests = [case([(2, 3), (4, 1)]), case([]), case([(5, 5)]), case([(-1, -2), (1, 0), (-1, -2)])]
		tests += [case(random_points(rng, -3, 3)) for _ in range(10)]
	else:
		tests = [case([(0, 0), (2, 1), (3, 0)], 3), case([], 2), case([(0, 1), (1, 0)], 2), case([(-1, 0)], 1)]
		tests += [case(random_points(rng, -1, 4), rng.randint(1, 5)) for _ in range(10)]
	return tests

RULES = {
	"count": ("points: list[tuple[int, int]], height: int, width: int", "takes points as\n"
		"(row, col) tuples, a height and a width, and returns a grid of height\n"
		"rows of width characters. A cell shows how many points fall on it: a dot\n"
		"for none, the digit for 1 to 9, + for 10 or more. Row 0 is the top one,\n"
		"column 0 the left one, and the points out of the grid are ignored"),
	"bounds": ("points: list[tuple[int, int]]", "takes points as (row, col) tuples, that may\n"
		"be negative, and returns the smallest rectangle that holds them all:\n"
		"its first row is the smallest row of a point and its last row the\n"
		"largest, and the same for the columns. A cell with a point shows *, the\n"
		"others a dot. No point gives an empty list"),
	"up": ("points: list[tuple[int, int]], size: int", "takes points as (x, y) tuples and a\n"
		"size, and returns a square grid of size rows of size characters, like a\n"
		"graph: x is the column, from 0 on the left, and y goes up, from 0 on the\n"
		"bottom row. A cell with a point shows *, the others a dot, and the\n"
		"points out of the grid are ignored"),
}

EXERCISE = Exercise(
	name="star_chart",
	language="python",
	kind="function",
	assignment_name="chart_${rule}",
	expected_files=("chart_${rule}.py",),
	allowed_functions=(),
	themes=("grid_plot",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that\n"
		"$rule.\n"
		"\n"
		"The grid is a list of strings, one for each row, from the top one.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("chart_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> list[str]:",
	examples=lambda params: {
		"count": (case([(0, 0), (0, 0), (1, 2), (5, 5)], 2, 3),),
		"bounds": (case([(2, 3), (4, 1)]), case([])),
		"up": (case([(0, 0), (2, 1), (3, 0)], 3),),
	}[params["rule"]],
)
