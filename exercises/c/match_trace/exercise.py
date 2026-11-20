"""match_trace: an original program model in the style of "a word made from another".

s1 can be made from s2 when all its characters are in s2, in the same order.
The program displays s2 with the characters used to make s1 in uppercase,
the characters of s2 that are not used, or the longest start of s1 that can
be made; letters in the exact case or in either case. s1 itself when it can
be made, a real 42 subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def used_places(s1, s2, same):
	"""The places in s2 of the characters of s1, each the first after the one before."""
	places = []
	i = 0
	for char in s1:
		while i < len(s2) and not same(s2[i], char):
			i += 1
		if i == len(s2):
			break
		places.append(i)
		i += 1
	return places

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 2:
		return "\n"
	s1, s2 = test.args
	if params["case"] == "any_case":
		same = lambda a, b: a.lower() == b.lower()
	else:
		same = lambda a, b: a == b
	places = used_places(s1, s2, same)
	what = params["what"]
	if what == "prefix":
		return s1[:len(places)] + "\n"
	if len(places) < len(s1):
		return "\n"
	if what == "marked":
		return "".join(char.upper() if i in places else char for i, char in enumerate(s2)) + "\n"
	return "".join(char for i, char in enumerate(s2) if i not in places) + "\n"

def generate_tests(params, rng):
	pairs = [("abc", "xaybzc"), ("abc", "acb"), ("faya", "fgvvfdxcacpolhyghbreda"), ("", "abc"),
		("ABC", "xaybzc"), ("hello", "hello"), ("xyz", "")]
	tests = [TestCase(args) for args in [(), ("a",), ("a", "b", "c")]]
	tests += [TestCase(pair) for pair in pairs]
	for _ in range(8):
		s2 = "".join(rng.choice("abcAB.") for _ in range(rng.randint(0, 12)))
		s1 = "".join(rng.choice("abcA") for _ in range(rng.randint(0, 4)))
		tests.append(TestCase((s1, s2)))
	return tests

EXERCISE = Exercise(
	name="match_trace",
	language="c",
	kind="program",
	assignment_name="match_${what}_${case}",
	expected_files=("match_${what}_${case}.c",),
	allowed_functions=("write",),
	themes=("hidden_word",),
	params=(
		Param("what", ("marked", "skipped", "prefix"), {
			"marked": "s2 with the characters used to make s1 in uppercase (the other ones as\n"
				"they are), if s1 can be made; only a newline otherwise",
			"skipped": "the characters of s2 that are not used to make s1, in their order, if\n"
				"s1 can be made; only a newline otherwise",
			"prefix": "the longest start of s1 that can be made from s2 (maybe empty)",
		}),
		Param("case", ("exact", "any_case"), {
			"exact": "Characters are compared exactly: a and A are different",
			"any_case": "A letter and its other case are the same: a and A match",
		}),
	),
	subject=(
		"Write a program that takes two strings, s1 and s2. s1 can be made from s2\n"
		"when its characters are all in s2, in the same order: each one is the first\n"
		"one after the one used before. The program displays\n"
		"$what,\n"
		"followed by a newline.\n"
		"$case.\n"
		"\n"
		"If the number of arguments is not 2, the program displays only a newline."
	),
	examples=(TestCase(("abc", "xaybzc")), TestCase(("abc", "acb")), TestCase(("a",))),
	oracle=oracle,
	generate_tests=generate_tests,
)
