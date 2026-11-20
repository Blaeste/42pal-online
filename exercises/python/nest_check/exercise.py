"""nest_check: an original Python model in the style of "check the brackets
of a string".

The student writes a function that reads the brackets of a string (two
kinds or four) and returns the number of pairs, the index of the first
bracket opened at the deepest level, or the string repaired with the
closing brackets it lacks. Saying only whether the brackets are right, a
real subject, is not one of the reports.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

BRACKETS = {"two": "()[]", "four": "()[]{}<>"}

def scan(text, brackets):
	"""Return (still_open, pairs, deepest), or None if a closing bracket is wrong."""
	openers, closers = brackets[0::2], brackets[1::2]
	stack, pairs, deepest, best = [], 0, -1, 0
	for index, char in enumerate(text):
		if char in openers:
			stack.append(char)
			if len(stack) > best:
				best, deepest = len(stack), index
		elif char in closers:
			if not stack or openers.index(stack[-1]) != closers.index(char):
				return None
			stack.pop()
			pairs += 1
	return stack, pairs, deepest

def oracle(params, test):
	(text,) = values(test)
	brackets = BRACKETS[params["kinds"]]
	found = scan(text, brackets)
	if params["report"] == "repair":
		if found is None:
			return shown(None)
		closers = {brackets[i]: brackets[i + 1] for i in range(0, len(brackets), 2)}
		return shown(text + "".join(closers[char] for char in reversed(found[0])))
	if found is None or found[0]:
		return shown(-1)
	return shown(found[1] if params["report"] == "pairs" else found[2])

def generate_tests(params, rng):
	texts = ["", "abc", "a(b[c])()", "([)]", "{<", "a(b[c])(d)", "<>{[()]}", "((", "({<a", "(]",
		"{x", ")(", "[(])", "<<>>{}"]
	for _ in range(10):
		texts.append("".join(rng.choice("()[]{}<>ab") for _ in range(rng.randint(1, 12))))
	return [case(text) for text in texts]

RETURNS = {"pairs": "int", "deepest": "int", "repair": "str | None"}

EXERCISE = Exercise(
	name="nest_check",
	language="python",
	kind="function",
	assignment_name="nest_${report}_${kinds}",
	expected_files=("nest_${report}_${kinds}.py",),
	allowed_functions=(),
	themes=("bracket_balance",),
	params=(
		Param("report", ("pairs", "deepest", "repair"), {
			"pairs": "the number of pairs of brackets in it if its brackets are right, or -1\n"
				"otherwise",
			"deepest": "the index of the first bracket opened at the deepest level (the first\n"
				"one that makes the most brackets open at the same time) if its brackets\n"
				"are right, or -1 otherwise or if it has no bracket",
			"repair": "the string followed by the closing brackets of the brackets still open,\n"
				"the last opened first, if no closing bracket is wrong; or None if one\n"
				"is (it closes nothing, or a bracket of another kind)",
		}),
		Param("kinds", ("two", "four"), {
			"two": "( ) and [ ] only: { } and < > are not brackets here",
			"four": "( ), [ ], { } and < >",
		}),
	),
	subject=(
		"Write a function that takes a string and returns\n"
		"$report.\n"
		"\n"
		"The brackets are $kinds; every other character is ignored. The brackets of\n"
		"a string are right when each closing bracket closes the last bracket\n"
		"opened and not closed yet, of the same kind, and no bracket is still open\n"
		"at the end. A string with no bracket is right.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("nest_${report}_${kinds}"),
	call=call,
	prototype=lambda name, params: f"def {name}(text: str) -> {RETURNS[params['report']]}:",
	# {a[b]c}< shows which characters are brackets: with two kinds, { } and <
	# are ignored; with four, the < is still open.
	examples=(case("a(b[c])(d)"), case("{a[b]c}<"), case("({<a"), case("([)]")),
)
