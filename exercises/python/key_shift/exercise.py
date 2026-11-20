"""key_shift: an original Python model in the style of "shift letters in
the alphabet".

The student writes a function that shifts letters: by the letters of a key
in turn, by a shift that grows with each letter, or with the digits shifted
too. One shift for every letter and nothing else, the real subject, is not
one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def shift_char(char, shift):
	for first, size in (("a", 26), ("A", 26)):
		if first <= char <= chr(ord(first) + 25):
			return chr(ord(first) + (ord(char) - ord(first) + shift) % size)
	return char

def oracle(params, test):
	text, how = values(test)
	rule = params["rule"]
	result, count = "", 0
	for char in text:
		if char.isascii() and char.isalpha():
			if rule == "by_key":
				shift = ord(how[count % len(how)].lower()) - ord("a")
			elif rule == "growing":
				shift = count * how
			else:
				shift = how
			result += shift_char(char, shift)
			count += 1
		elif rule == "with_digits" and char.isdigit():
			result += str((int(char) + how) % 10)
		else:
			result += char
	return shown(result)

def generate_tests(params, rng):
	texts = ["Hello, World", "aaa-a", "Zz", "Zz 09!", "a0", "", "xyz XYZ 789", "The 42 cats."]
	tests = []
	for index, text in enumerate(texts + ["".join(rng.choice("abzAZ 5.") for _ in range(rng.randint(1, 12)))
			for _ in range(10)]):
		if params["rule"] == "by_key":
			key = "abc" if index < 3 else "".join(rng.choice("abzKQ") for _ in range(rng.randint(1, 4)))
			tests.append(case(text, key))
		else:
			tests.append(case(text, rng.randint(-30, 30) if index > 4 else (2, -1, 3, -1, 25)[index]))
	return tests

RULES = {
	"by_key": ("text: str, key: str", "each letter is shifted by the value of a letter of key,\n"
		"a being 0, b being 1, up to z for 25, in either case. The letters of key\n"
		"are used in turn: the first letter of text by the first letter of key,\n"
		"the second by the second, and so on, starting key again when it ends.\n"
		"key is never empty and holds letters only. The characters of text that\n"
		"are not letters use no letter of key"),
	"growing": ("text: str, step: int", "the first letter is shifted by 0, the second by step,\n"
		"the third by 2 times step, and so on: the letter number n, counting\n"
		"from 0, is shifted by n times step. step may be negative"),
	"with_digits": ("text: str, shift: int", "each letter is shifted by shift, and each digit too,\n"
		"among the digits: 9 shifted by 1 gives 0. shift may be negative"),
}

EXERCISE = Exercise(
	name="key_shift",
	language="python",
	kind="function",
	assignment_name="shift_${rule}",
	expected_files=("shift_${rule}.py",),
	allowed_functions=(),
	themes=("letter_shift",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that returns a copy of the string text where\n"
		"$rule.\n"
		"\n"
		"A letter is shifted among the letters of its case: z shifted by 1 gives a,\n"
		"Z gives A, and a shifted by -1 gives z. The letters are a to z and A to Z;\n"
		"the other characters stay as they are.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("shift_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> str:",
	examples=lambda params: {
		"by_key": (case("Hello, World", "abc"), case("Zz", "B")),
		"growing": (case("aaa-a", 2), case("Zz", -1)),
		"with_digits": (case("Zz 09!", 3), case("a0", -1)),
	}[params["rule"]],
)
