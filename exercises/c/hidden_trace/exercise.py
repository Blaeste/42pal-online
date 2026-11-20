"""hidden_trace: an original program model in the style of "a string hidden in another".

s1 is hidden in s2 when its characters are all in s2, in the same order,
maybe with other characters between them. The program displays where they
are found first, the length of the shortest part of s2 that hides s1, or
whether s1 is hidden in s2 read backwards; letters in the exact case or in
either case. Whether s1 is hidden in s2 read forwards, a real 42 subject, is
not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase

def first_places(s1, s2, start=0):
	"""Where the characters of s1 are found first in s2 from `start`, or None."""
	places = []
	i = start
	for char in s1:
		while i < len(s2) and s2[i] != char:
			i += 1
		if i == len(s2):
			return None
		places.append(i)
		i += 1
	return places

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 2:
		return "\n"
	s1, s2 = test.args
	if params["case"] == "any_case":
		s1, s2 = s1.lower(), s2.lower()
	what = params["what"]
	if what == "positions":
		places = first_places(s1, s2)
		return " ".join(map(str, places)) + "\n" if places else "\n"
	if what == "backwards":
		return f"{int(first_places(s1, s2[::-1]) is not None)}\n"
	if not s1:
		return "0\n"
	windows = [places[-1] - places[0] + 1 for start in range(len(s2))
		if s2[start] == s1[0] and (places := first_places(s1, s2, start)) is not None]
	return f"{min(windows, default=0)}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed pairs, then random ones."""
	pairs = [("abc", "xaxbxc"), ("cba", "xaxbxc"), ("ab", "aXXabYb"), ("AB", "xaxB"),
		("abc", "acb"), ("", "abc"), ("", ""), ("abc", ""), ("same", "same"), ("aaa", "aaaa")]
	tests = [TestCase(args) for args in [(), ("a",), ("a", "b", "c")]]
	tests += [TestCase(pair) for pair in pairs]
	for _ in range(8):
		s2 = "".join(rng.choice("abcAB") for _ in range(rng.randint(0, 12)))
		s1 = "".join(rng.choice("abcAB") for _ in range(rng.randint(0, 3)))
		tests.append(TestCase((s1, s2)))
	return tests

EXERCISE = Exercise(
	name="hidden_trace",
	language="c",
	kind="program",
	assignment_name="hidden_${what}_${case}",
	expected_files=("hidden_${what}_${case}.c",),
	allowed_functions=("write",),
	themes=("hidden_order",),
	params=(
		Param("what", ("positions", "window", "backwards"), {
			"positions": "where the characters of s1 are found in s2: for each one, in order,\n"
				"the first index in s2 after the one found before (indexes from 0,\n"
				"separated by spaces); nothing if s1 is not hidden in s2 or is empty",
			"window": "the length of the shortest part of s2 (characters next to each\n"
				"other) in which s1 is hidden; 0 if s1 is not hidden in s2 or is empty",
			"backwards": "1 if s1 is hidden in s2 read from its last character to its first,\n"
				"0 otherwise (an empty s1 is hidden everywhere)",
		}),
		Param("case", ("exact", "any_case"), {
			"exact": "Characters are compared exactly: a and A are different",
			"any_case": "A letter and its other case are the same: a and A match",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes two strings, s1 and s2. s1 is hidden in s2 when\n"
		"all its characters are in s2, in the same order, maybe with other\n"
		"characters between them. The program displays\n"
		"$what,\n"
		"followed by a newline.\n"
		"$case.\n"
		"\n"
		"If the number of arguments is not 2, the program displays only a newline."
	),
	examples=(TestCase(("abc", "xaxbxc")), TestCase(("ab", "aXXabYb")), TestCase(("a",))),
	oracle=oracle,
	generate_tests=generate_tests,
)
