"""slot_share: an original Python model in the style of "share out time
intervals".

The student writes a function that reads meetings given as [start, end]
intervals: the busy times merged, the free gaps of a day, or when the most
meetings happen at once. The fewest rooms and the schedule of each room,
the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def merged(meetings):
	result = []
	for start, end in sorted(meetings):
		if result and start <= result[-1][1]:
			result[-1][1] = max(result[-1][1], end)
		else:
			result.append([start, end])
	return result

def oracle(params, test):
	rule = params["rule"]
	if rule == "gaps":
		meetings, day_start, day_end = values(test)
		gaps, now = [], day_start
		for start, end in merged(meetings):
			start, end = max(start, day_start), min(end, day_end)
			if start >= end:
				continue
			if start > now:
				gaps.append([now, start])
			now = max(now, end)
		if now < day_end:
			gaps.append([now, day_end])
		return shown(gaps)
	(meetings,) = values(test)
	if rule == "merge":
		return shown(merged(meetings))
	best = [0, 0]
	for time in sorted({start for start, _ in meetings}):
		count = sum(1 for start, end in meetings if start <= time < end)
		if count > best[1]:
			best = [time, count]
	return shown(best)

def random_meetings(rng):
	meetings = []
	for _ in range(rng.randint(0, 6)):
		start = rng.randint(0, 20)
		meetings.append([start, start + rng.randint(1, 6)])
	return meetings

def generate_tests(params, rng):
	fixed = [[[1, 3], [2, 6], [8, 10], [10, 12], [15, 18]], [[1, 3], [3, 5]], [], [[5, 9]],
		[[4, 8], [1, 2], [2, 4]], [[1, 10], [2, 3], [4, 5], [2, 5]]]
	groups = fixed + [random_meetings(rng) for _ in range(10)]
	if params["rule"] != "gaps":
		return [case(group) for group in groups]
	days = [(0, 16), (0, 6), (9, 17), (6, 8), (0, 10), (3, 4)] + [(rng.randint(0, 8), rng.randint(9, 25))
		for _ in range(10)]
	return [case(group, start, end) for group, (start, end) in zip(groups, days)]

RULES = {
	"merge": ("meetings: list[list[int]]", "list[list[int]]", "returns the times when at least\n"
		"one meeting is going on, as a list of [start, end] intervals sorted by\n"
		"start: meetings that overlap or follow each other with no gap are merged\n"
		"into one interval"),
	"gaps": ("meetings: list[list[int]], day_start: int, day_end: int", "list[list[int]]",
		"also takes a day, from day_start to day_end (day_start before day_end),\n"
		"and returns the free times of that day, when no meeting is going on, as\n"
		"a list of [start, end] intervals sorted by start. A meeting may start\n"
		"before the day or end after it"),
	"busiest": ("meetings: list[list[int]]", "list[int]", "returns [time, count]: count is the\n"
		"largest number of meetings going on at the same time, and time the\n"
		"earliest time when that many are going on; [0, 0] if there is no\n"
		"meeting"),
}

EXERCISE = Exercise(
	name="slot_share",
	language="python",
	kind="function",
	assignment_name="slots_${rule}",
	expected_files=("slots_${rule}.py",),
	allowed_functions=(),
	themes=("interval_rooms",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that takes a list of meetings, each one a [start, end]\n"
		"list of two ints, start before end, in any order. A meeting is going on\n"
		"from its start up to its end, the end left out: [1, 3] and [3, 5] do not\n"
		"overlap. The function\n"
		"$rule.\n"
		"\n"
		"The given list must not be changed.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("slots_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"merge": (case([[1, 3], [2, 6], [8, 10], [10, 12], [15, 18]]),),
		"gaps": (case([[1, 3], [2, 6], [8, 10], [10, 12], [15, 18]], 0, 16),),
		"busiest": (case([[1, 3], [2, 6], [8, 10], [10, 12]]), case([])),
	}[params["rule"]],
)
