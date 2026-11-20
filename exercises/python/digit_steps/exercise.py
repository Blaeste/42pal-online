"""digit_steps: an original Python model in the style of "count patterns of
neighbouring digits".

The student writes a function that looks at the digits next to each other
in a string: pairs that go down by one, equal pairs, the longest run going
up by one, or pairs going up by one where 9 then 0 counts too. Pairs going
up by one without 9 then 0, the real subject, is not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def pairs(text):
	"""The pairs of digits next to each other in text, as ints."""
	return [(int(a), int(b)) for a, b in zip(text, text[1:]) if a.isdigit() and b.isdigit()]

def longest_run(text):
	best = current = 0
	for index, char in enumerate(text):
		if not char.isdigit():
			current = 0
			continue
		before = text[index - 1] if index else ""
		current = current + 1 if before.isdigit() and int(char) == int(before) + 1 else 1
		best = max(best, current)
	return best

def oracle(params, test):
	(text,) = values(test)
	rule = params["rule"]
	if rule == "longest_run":
		return shown(longest_run(text))
	step = {"down": lambda a, b: b == a - 1, "equal": lambda a, b: a == b,
		"wrap_up": lambda a, b: b == (a + 1) % 10}[rule]
	return shown(sum(1 for a, b in pairs(text) if step(a, b)))

def generate_tests(params, rng):
	texts = ["", "none", "3210a98", "111x22", "x1234y56", "97", "8901 23", "90", "09", "5", "0123456789"]
	for _ in range(10):
		texts.append("".join(rng.choice("0123456789 a") for _ in range(rng.randint(1, 14))))
	return [case(text) for text in texts]

EXERCISE = Exercise(
	name="digit_steps",
	language="python",
	kind="function",
	assignment_name="steps_${rule}",
	expected_files=("steps_${rule}.py",),
	allowed_functions=(),
	themes=("digit_pairs",),
	params=(
		Param("rule", ("down", "equal", "longest_run", "wrap_up"), {
			"down": "the number of pairs of digits next to each other where the second digit\n"
				"is one less than the first one (1 then 0 counts, 0 then 9 does not)",
			"equal": "the number of pairs of digits next to each other that are the same\n"
				"digit (111 holds two pairs)",
			"longest_run": "the length of the longest group of digits next to each other where\n"
				"each digit is one more than the one before it (1234 is such a group of\n"
				"4); 1 if no two digits make such a pair, and 0 if there is no digit",
			"wrap_up": "the number of pairs of digits next to each other where the second digit\n"
				"is one more than the first one, 9 then 0 counting too",
		}),
	),
	subject=(
		"Write a function that takes a string and returns\n"
		"$rule.\n"
		"\n"
		"Two characters are next to each other when nothing is between them in the\n"
		"string; a pair of digits overlaps the next one (123 holds the pairs 12 and\n"
		"23).\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(text: str) -> int:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("steps_${rule}"),
	call=call,
	examples=(case("3210a98"), case("x1234y56"), case("8901 23")),
)
