"""zone_fill: an original function model in the style of "fill an area of a grid".

The zone of a cell is the cell and every cell of the same character joined
to it, through four or eight neighbours. The function fills the zone with F,
or measures it (its size, or how many of its cells touch the border of the
grid). Filling with four neighbours, a real 42 subject, is left out.
"""

from collections import deque

from pal42.model import Exercise, Param, TestCase

def zone_cells(rows, x, y, connect):
	"""The cells (column, row) of the zone of (x, y)."""
	width, height = len(rows[0]), len(rows)
	target = rows[y][x]
	steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	if connect == "eight":
		steps += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
	seen = {(x, y)}
	waiting = deque([(x, y)])
	while waiting:
		cx, cy = waiting.popleft()
		for dx, dy in steps:
			nx, ny = cx + dx, cy + dy
			if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and rows[ny][nx] == target:
				seen.add((nx, ny))
				waiting.append((nx, ny))
	return seen

def oracle(params, test):
	"""Return what the test main prints: the grid after the call, then the int returned."""
	x, y = int(test.args[0]), int(test.args[1])
	rows = [list(row) for row in test.args[2:]]
	cells = zone_cells(test.args[2:], x, y, params["connect"])
	measure = params["measure"]
	if measure == "fill":
		for cx, cy in cells:
			rows[cy][cx] = "F"
		result = len(cells)
	elif measure == "size":
		result = len(cells)
	else:
		width, height = len(rows[0]), len(rows)
		result = sum(1 for cx, cy in cells if cx in (0, width - 1) or cy in (0, height - 1))
	return "".join("".join(row) + "\n" for row in rows) + f"{result}\n"

def generate_tests(params, rng):
	"""Return the test cases: grids with a clear answer first, then random ones."""
	grids = [
		(0, 0, ("1001", "0110", "1001")),
		(1, 0, ("1001", "0110", "1001")),
		(0, 0, ("11100", "10100", "11001")),
		(1, 2, ("ab", "ab", "aa")),
		(0, 0, ("x",)),
		(3, 2, ("....#", ".##.#", "#..##", "....#")),
		(1, 1, ("FFF", "FFF", "FFF")),
	]
	for _ in range(8):
		width, height = rng.randint(1, 9), rng.randint(1, 6)
		rows = tuple("".join(rng.choice("01") for _ in range(width)) for _ in range(height))
		grids.append((rng.randrange(width), rng.randrange(height), rows))
	return [TestCase((str(x), str(y), *rows)) for x, y, rows in grids]

# The test main: av[1] and av[2] are x and y, the next ones the rows of the
# grid; it prints the grid after the call, then the int returned.
HARNESS = """#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int	ft_zone_${connect}_${measure}(char **grid, int width, int height, int x, int y);

int	main(int ac, char **av)
{
	char	**grid;
	int		height;
	int		result;
	int		i;

	height = ac - 3;
	grid = malloc(sizeof(char *) * height);
	i = 0;
	while (i < height)
	{
		grid[i] = strdup(av[i + 3]);
		i++;
	}
	result = ft_zone_${connect}_${measure}(grid, strlen(av[3]), height,
			atoi(av[1]), atoi(av[2]));
	i = 0;
	while (i < height)
	{
		printf("%s\\n", grid[i]);
		free(grid[i++]);
	}
	free(grid);
	printf("%d\\n", result);
	return (0);
}
"""

def call(name, test):
	"""The call shown in the examples and the traces, with the grid in a comment."""
	rows = test.args[2:]
	return f"{name}(grid, {len(rows[0])}, {len(rows)}, {test.args[0]}, {test.args[1]}) /* {' / '.join(rows)} */"

EXERCISE = Exercise(
	name="zone_fill",
	language="c",
	kind="function",
	assignment_name="ft_zone_${connect}_${measure}",
	expected_files=("ft_zone_${connect}_${measure}.c",),
	allowed_functions=(),
	themes=("grid_fill",),
	params=(
		Param("connect", ("four", "eight"), {
			"four": "its four neighbours (up, down, left and right)",
			"eight": "its eight neighbours (up, down, left, right and the four diagonals)",
		}),
		Param("measure", ("fill", "size", "edge"), {
			"fill": "replaces every cell of the zone by the character F, and returns how\n"
				"many cells it replaced",
			"size": "returns how many cells the zone has, and leaves the grid as it is",
			"edge": "returns how many cells of the zone are on the edge of the grid (in its\n"
				"first or last row, or in its first or last column), and leaves the grid\n"
				"as it is",
		}),
	),
	# Filling with four neighbours: a real subject.
	forbidden=({"connect": "four", "measure": "fill"},),
	subject=(
		"Write a function that takes a grid of characters and the place (x, y) of one\n"
		"of its cells, and works on the zone of that cell.\n"
		"\n"
		"The grid has height rows of width characters. grid[y][x] is the cell at\n"
		"column x and row y, both counted from 0. The zone of a cell is that cell\n"
		"and all the cells of the same character that can be reached from it, step\n"
		"by step: each step goes to one of $connect, and every cell on the way has\n"
		"that same character.\n"
		"\n"
		"The function $measure.\n"
		"\n"
		"(x, y) is always in the grid, and the grid is at most 50 by 50.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char **grid, int width, int height, int x, int y);\n"
		"\n"
		"In the examples, the comment shows the rows of the grid before the call,\n"
		"separated by /. The lines below show the grid after the call, then the int\n"
		"returned."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=call,
	examples=(TestCase(("0", "0", "1001", "0110", "1001")), TestCase(("1", "0", "1001", "0110", "1001"))),
)
