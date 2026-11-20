"""longest_span: an original program model on the theme "search a string".

The program displays the longest part of a string (characters next to each
other) with no character twice, that appears twice, whose characters are
sorted, or made of two characters at most: the first or the last one of the
longest. The longest palindrome, a real 42 subject, is not one of the rules.
"""

from pal42.model import Exercise, Param, TestCase

def follows(rule, text, start, length):
	"""True if the part of `text` at `start`, `length` long, follows `rule`."""
	part = text[start:start + length]
	if rule == "unique":
		return len(set(part)) == len(part)
	if rule == "sorted":
		return all(a <= b for a, b in zip(part, part[1:]))
	if rule == "two_chars":
		return len(set(part)) <= 2
	# repeated: the same part starts somewhere else too (it may overlap).
	return any(text.startswith(part, other)
		for other in range(len(text) - length + 1) if other != start)

def longest(rule, tie, text):
	"""The longest part that follows `rule`: the first or the last one; "" if none."""
	for length in range(len(text), 0, -1):
		starts = [start for start in range(len(text) - length + 1)
			if follows(rule, text, start, length)]
		if starts:
			start = starts[0] if tie == "first" else starts[-1]
			return text[start:start + length]
	return ""

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	return longest(params["rule"], params["tie"], test.args[0]) + "\n"

def generate_tests(params, rng):
	"""Return the test cases of a variant: fixed strings, then random ones."""
	tests = [TestCase(()), TestCase(("a", "b")), TestCase(("",)), TestCase(("z",))]
	for text in ["pwwkew", "banana", "xyzxyabab", "abcd", "dabcxyab", "acbd", "aabbccdd",
			"eceba", "aaaa", "to be or not to be"]:
		tests.append(TestCase((text,)))
	for _ in range(8):
		alphabet = rng.choice(["ab", "abc", "abcdxyz", "aab c"])
		tests.append(TestCase(("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 24))),)))
	return tests

EXERCISE = Exercise(
	name="longest_span",
	language="c",
	kind="program",
	assignment_name="longest_${rule}_${tie}",
	expected_files=("longest_${rule}_${tie}.c",),
	allowed_functions=("write",),
	themes=("longest_part",),
	params=(
		Param("rule", ("unique", "repeated", "sorted", "two_chars"), {
			"unique": "in which no character appears twice",
			"repeated": "that appears at least twice in the string (the two may overlap,\n"
				"like ana in banana)",
			"sorted": "whose characters are in increasing ASCII order (a character may come\n"
				"several times in a row, like in abbcz)",
			"two_chars": "made of two different characters at most, like aabaa",
		}),
		Param("tie", ("first", "last"), {
			"first": "it displays the one that starts first",
			"last": "it displays the one that starts last",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes one string and displays its longest part\n"
		"$rule,\n"
		"followed by a newline. A part is a run of characters next to each other in\n"
		"the string; the whole string is one of them. If several parts are the\n"
		"longest,\n"
		"$tie.\n"
		"The string has at most 100 characters.\n"
		"\n"
		"If no part is such, or if the number of arguments is not 1, the program\n"
		"displays only a newline."
	),
	examples=(
		TestCase(("pwwkew",)),
		TestCase(("xyzxyabab",)),
		TestCase(("to be or not to be",)),
	),
	oracle=oracle,
	generate_tests=generate_tests,
)
