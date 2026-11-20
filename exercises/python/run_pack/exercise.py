"""run_pack: an original Python model in the style of "encode and decode runs
of characters".

The student writes a function about runs of the same character: the runs as
(character, length) pairs, a packed string with each length before its
character, or the reverse of that packing. Lengths written after the
characters, the real subject, is not one of the rules.
"""

import re
from itertools import groupby

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def runs(text):
	return [(char, len(list(group))) for char, group in groupby(text)]

def oracle(params, test):
	(text,) = values(test)
	rule = params["rule"]
	if rule == "pairs":
		return shown(runs(text))
	if rule == "count_first":
		return shown("".join((str(size) if size > 1 else "") + char for char, size in runs(text)))
	return shown("".join(char * int(size or 1) for size, char in re.findall(r"(\d*)(\D)", text)))

def packed(text):
	return "".join((str(size) if size > 1 else "") + char for char, size in runs(text))

def generate_tests(params, rng):
	texts = ["", "aaabcc", "z" * 12, "abc", "a", "  !!", "aabbaa", "xxxxxxxxxxy"]
	for _ in range(10):
		texts.append("".join(rng.choice("ab -") * rng.randint(1, 4) for _ in range(rng.randint(1, 6))))
	if params["rule"] == "expand":
		texts = [packed(text) for text in texts]
	return [case(text) for text in texts]

RULES = {
	"pairs": ("text: str", "list[tuple[str, int]]", "takes a string and returns its runs, in\n"
		"order, as a list of (character, length) tuples"),
	"count_first": ("text: str", "str", "takes a string that holds no digit and returns it\n"
		"packed: each run written as its length, then its character, the length\n"
		"left out when it is 1 (aaabcc gives 3ab2c)"),
	"expand": ("packed: str", "str", "takes a string packed that way (each run written as its\n"
		"length, then its character, the length left out when it is 1; a length\n"
		"may have several digits) and returns the string it was made from (3ab2c\n"
		"gives aaabcc)"),
}

EXERCISE = Exercise(
	name="run_pack",
	language="python",
	kind="function",
	assignment_name="runs_${rule}",
	expected_files=("runs_${rule}.py",),
	allowed_functions=(),
	themes=("run_length",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"A run is a group of the same character repeated, next to each other, as\n"
		"long as it can be: aaabcc has the runs aaa, b and cc. Write a function that\n"
		"$rule.\n"
		"\n"
		"An empty string has no run.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("runs_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"pairs": (case("aaabcc"), case("")),
		"count_first": (case("aaabcc"), case("z" * 12)),
		"expand": (case("3ab2c"), case("12z")),
	}[params["rule"]],
)
