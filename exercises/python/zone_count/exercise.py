"""zone_count: an original Python model in the style of "count the regions of
a grid".

The student writes a function that explores a grid of land (#) and water
(.): the size of the largest island, the islands when corners join too, the
lakes closed in by land, or the length of the coast. The number of islands
of a grid of "1" and "0", the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

SIDES = ((0, 1), (1, 0), (0, -1), (-1, 0))
AROUND = SIDES + ((1, 1), (1, -1), (-1, 1), (-1, -1))

def regions(grid, kind, steps):
	"""The regions of cells equal to kind, joined by the steps: lists of cells."""
	seen, found = set(), []
	for row, line in enumerate(grid):
		for col, char in enumerate(line):
			if char != kind or (row, col) in seen:
				continue
			region, todo = [], [(row, col)]
			seen.add((row, col))
			while todo:
				r, c = todo.pop()
				region.append((r, c))
				for dr, dc in steps:
					nr, nc = r + dr, c + dc
					if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == kind \
							and (nr, nc) not in seen:
						seen.add((nr, nc))
						todo.append((nr, nc))
			found.append(region)
	return found

def oracle(params, test):
	(grid,) = values(test)
	rule = params["rule"]
	if rule == "largest":
		return shown(max((len(region) for region in regions(grid, "#", SIDES)), default=0))
	if rule == "diagonal":
		return shown(len(regions(grid, "#", AROUND)))
	if rule == "lakes":
		edge = lambda r, c: r in (0, len(grid) - 1) or c in (0, len(grid[0]) - 1)
		return shown(sum(1 for region in regions(grid, ".", SIDES) if not any(edge(r, c) for r, c in region)))
	coast = 0
	for row, line in enumerate(grid):
		for col, char in enumerate(line):
			if char == "#":
				for dr, dc in SIDES:
					nr, nc = row + dr, col + dc
					if not (0 <= nr < len(grid) and 0 <= nc < len(line)) or grid[nr][nc] != "#":
						coast += 1
	return shown(coast)

def generate_tests(params, rng):
	grids = [["##..", "#..#", "..##", "#..."], ["#.#", ".#.", "#.."], ["#####", "#..##", "#####", "#.#.#"],
		["##", "#."], ["#"], ["."], [], ["###", "#.#", "###"], ["....", ".##.", "...."]]
	for _ in range(10):
		width = rng.randint(1, 7)
		grids.append(["".join(rng.choice("#.") for _ in range(width)) for _ in range(rng.randint(1, 6))])
	return [case(grid) for grid in grids]

EXERCISE = Exercise(
	name="zone_count",
	language="python",
	kind="function",
	assignment_name="zone_${rule}",
	expected_files=("zone_${rule}.py",),
	allowed_functions=(),
	themes=("grid_regions",),
	params=(
		Param("rule", ("largest", "diagonal", "lakes", "perimeter"), {
			"largest": "the number of cells of the largest island (0 if there is no land)",
			"diagonal": "the number of islands, when two land cells that touch by a corner are\n"
				"joined too",
			"lakes": "the number of lakes: regions of water cells joined by their sides that\n"
				"touch no edge of the grid",
			"perimeter": "the length of the coast: the number of sides of land cells that touch\n"
				"a water cell or the edge of the grid",
		}),
	),
	subject=(
		"Write a function that takes a map: a list of strings of the same length,\n"
		"made of # for land and . for water (an empty list is an empty map). An\n"
		"island is a group of land cells joined by their sides, as large as it can\n"
		"be. The function returns\n"
		"$rule.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(grid: list[str]) -> int:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("zone_${rule}"),
	call=call,
	examples=(case(["##..", "#..#", "..##", "#..."]), case(["#.#", ".#.", "#.."]), case(["###", "#.#", "###"])),
)
