"""nest_report: an original program model on the theme "parse with a stack".

The program reads the brackets of each of its arguments (round ones only,
three kinds or four) and displays, for each one, the largest number of
brackets open at once, the index of the first wrong bracket, or the string
completed with the closing brackets it lacks. Saying only whether the
brackets are right, a real 42 subject, is not one of the reports.
"""

from pal42.model import Exercise, Param, TestCase

# Each kind of bracket: its opening and closing characters side by side.
BRACKETS = {"round": "()", "three": "()[]{}", "four": "()[]{}<>"}

def scan(text, brackets):
	"""Read the brackets of `text`: ("right", depth), ("wrong", index) or ("open", stack).

	stack holds (character, index) of the brackets still open, the last
	opened at the end.
	"""
	openers, closers = brackets[0::2], brackets[1::2]
	stack = []
	depth = 0
	for index, char in enumerate(text):
		if char in openers:
			stack.append((char, index))
			depth = max(depth, len(stack))
		elif char in closers:
			if not stack or openers.index(stack[-1][0]) != closers.index(char):
				return "wrong", index
			stack.pop()
	if stack:
		return "open", stack
	return "right", depth

def line(text, report, brackets):
	"""The line displayed for one string."""
	state, detail = scan(text, brackets)
	if report == "depth":
		return str(detail) if state == "right" else "Error"
	if report == "error_at":
		if state == "right":
			return "OK"
		return str(detail if state == "wrong" else detail[-1][1])
	if state == "wrong":
		return "Error"
	if state == "open":
		closers = brackets[1::2]
		openers = brackets[0::2]
		return text + "".join(closers[openers.index(char)] for char, _ in reversed(detail))
	return text

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if not test.args:
		return "\n"
	return "".join(line(text, params["report"], BRACKETS[params["brackets"]]) + "\n"
		for text in test.args)

def random_text(rng, brackets, depth=2):
	"""A short string of brackets and letters, right or not, nested `depth` times at most."""
	if depth > 0 and rng.randint(0, 1):
		# Built right: each bracket opened is closed, then maybe broken.
		text = ""
		for _ in range(rng.randint(1, 3)):
			kind = rng.randrange(len(brackets) // 2)
			if rng.randint(0, 1):
				inside = random_text(rng, brackets, depth - 1)
			else:
				inside = rng.choice(["", "a", "xy"])
			text += brackets[2 * kind] + inside + brackets[2 * kind + 1]
		if rng.randint(0, 2) == 0:
			cut = rng.randrange(len(text))
			text = text[:cut] + text[cut + 1:]
		return text
	return "".join(rng.choice(brackets + "ab ") for _ in range(rng.randint(1, 12)))

def generate_tests(params, rng):
	"""Return the test cases: fixed strings first, then random ones, several per run."""
	tests = [
		TestCase(()),
		TestCase(("",)),
		TestCase(("no bracket",)),
		TestCase(("(a(b)c)", "(()", "())")),
		TestCase(("{[()]}", "([)]", "<{[(x", "a)", "{[]")),
		TestCase(("<b>(i)</b>", "(]", "((((", "))))")),
	]
	for _ in range(8):
		count = rng.randint(1, 4)
		tests.append(TestCase(tuple(random_text(rng, BRACKETS["four"]) for _ in range(count))))
	return tests

EXERCISE = Exercise(
	name="nest_report",
	language="c",
	kind="program",
	assignment_name="nest_${report}_${brackets}",
	expected_files=("nest_${report}_${brackets}.c",),
	allowed_functions=("write",),
	themes=("bracket_check",),
	params=(
		Param("report", ("depth", "error_at", "complete"), {
			"depth": "the largest number of brackets open at the same time (0 for none)\n"
				"if its brackets are right, or Error otherwise",
			"error_at": "OK if its brackets are right; otherwise the index, from 0, of the\n"
				"first wrong bracket: a closing bracket that closes nothing or a bracket\n"
				"of another kind, or, when the string ends, the last bracket opened that\n"
				"is still open",
			"complete": "the string followed by the closing brackets that close the brackets\n"
				"still open, the last opened first; or Error if a closing bracket closes\n"
				"nothing or a bracket of another kind",
		}),
		Param("brackets", ("round", "three", "four"), {
			"round": "( and ) only",
			"three": "(), [] and {}",
			"four": "(), [], {} and <>",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes any number of strings and displays one line\n"
		"for each, about its brackets. The brackets are\n"
		"$brackets;\n"
		"every other character is ignored. The brackets of a string are right when\n"
		"each closing bracket closes the last bracket opened and not closed yet, of\n"
		"the same kind, and no bracket is still open at the end. A string with no\n"
		"bracket is right. Each string has at most 1000 characters.\n"
		"\n"
		"The line displayed for a string is\n"
		"$report.\n"
		"\n"
		"If there is no argument, the program displays only a newline."
	),
	examples=(
		TestCase(("{[(a)]}", "([)]", "((x")),
		TestCase(("<b>(i)</b>",)),
		TestCase(()),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
