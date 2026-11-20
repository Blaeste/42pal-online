"""window_stat: an original Python model in the style of "compute a value
over each window of a list".

The student writes a function that slides a window of k values along a
list and gives, for each place, its smallest value, its spread, its number
of different values, or its first negative value. The largest value of
each window, the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

RULES_OF = {
	"min": min,
	"spread": lambda window: max(window) - min(window),
	"distinct": lambda window: len(set(window)),
	"first_negative": lambda window: next((value for value in window if value < 0), 0),
}

def oracle(params, test):
	nums, k = values(test)
	if not 1 <= k <= len(nums):
		return shown([])
	return shown([RULES_OF[params["rule"]](nums[start:start + k]) for start in range(len(nums) - k + 1)])

def generate_tests(params, rng):
	pairs = [([1, 3, -1, -3, 5, 3], 3), ([2, 2, 3, 2], 2), ([1, 2], 3), ([1, 2], 0), ([], 1), ([7], 1),
		([4, -2, 5, -2, 1], 5), ([0, 0, 0], 2)]
	for _ in range(10):
		nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 10))]
		pairs.append((nums, rng.randint(1, len(nums))))
	return [case(nums, k) for nums, k in pairs]

EXERCISE = Exercise(
	name="window_stat",
	language="python",
	kind="function",
	assignment_name="window_${rule}",
	expected_files=("window_${rule}.py",),
	allowed_functions=(),
	themes=("window_max",),
	params=(
		Param("rule", tuple(RULES_OF), {
			"min": "its smallest value",
			"spread": "its largest value minus its smallest value",
			"distinct": "how many different values it holds",
			"first_negative": "its first negative value, from the left, or 0 if it has none",
		}),
	),
	subject=(
		"Write a function that takes a list of ints nums and an int k. A window is k\n"
		"values next to each other in nums: with k = 3, [1, 2, 3, 4] has the windows\n"
		"[1, 2, 3] and [2, 3, 4]. The function returns a list with, for each window,\n"
		"from the first one,\n"
		"$rule.\n"
		"\n"
		"If k is less than 1 or more than the length of nums, there is no window:\n"
		"the function returns an empty list. The given list must not be changed.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(nums: list[int], k: int) -> list[int]:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("window_${rule}"),
	call=call,
	examples=(case([1, 3, -1, -3, 5, 3], 3), case([2, 2, 3, 2], 2), case([1, 2], 3)),
)
