"""Reference solution of slot_share, for every variant: one function each.

Each meeting gives two events, +1 at its start and -1 at its end; going
through the events in order tells how many meetings are going on.
"""

def _events(meetings):
	events = []
	for start, end in meetings:
		events.append((start, 1))
		events.append((end, -1))
	# At the same time, the ends come before the starts: [1, 3] and [3, 5] do not overlap.
	return sorted(events, key=lambda event: (event[0], event[1]))

def slots_merge(meetings):
	result = []
	going = 0
	start = None
	events = _events(meetings)
	for index, (time, change) in enumerate(events):
		if going == 0 and change == 1:
			if result and result[-1][1] == time:
				start = result.pop()[0]
			else:
				start = time
		going += change
		if going == 0:
			result.append([start, time])
	return result

def slots_gaps(meetings, day_start, day_end):
	gaps = []
	now = day_start
	for start, end in slots_merge(meetings):
		if end <= now or start >= day_end:
			continue
		if start > now:
			gaps.append([now, start])
		now = max(now, end)
	if now < day_end:
		gaps.append([now, day_end])
	return gaps

def slots_busiest(meetings):
	best_time, best_count = 0, 0
	going = 0
	for time, change in _events(meetings):
		going += change
		if going > best_count:
			best_time, best_count = time, going
	return [best_time, best_count]
