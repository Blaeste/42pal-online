"""case_wave: an original Python model in the style of "change the case of
letters by their position".

The student writes a function that puts letters in upper or lower case by
their place: alternating again in each word, following a pattern of u and
l, or by the index of each character. Alternating over the letters of the
whole string from a lower case one, the real subject, is not one of the
rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def is_letter(char):
	return char.isascii() and char.isalpha()

def waved(text, rule, pattern=""):
	result, count = [], 0
	for index, char in enumerate(text):
		if rule == "words" and char == " ":
			count = 0
		if not is_letter(char):
			result.append(char)
			continue
		if rule == "all_chars":
			upper = index % 2 == 0
		elif rule == "words":
			upper = count % 2 == 0
		else:
			upper = pattern[count % len(pattern)] == "u"
		result.append(char.upper() if upper else char.lower())
		count += 1
	return "".join(result)

def oracle(params, test):
	return shown(waved(*values(test)[:1], params["rule"], *values(test)[1:]))

def generate_tests(params, rng):
	texts = ["", "hello big world", "a-bcd e", "abcd ef", "ALL UPPER", "x", "  two  spaces ",
		"it's 42, ok?"]
	for _ in range(10):
		texts.append("".join(rng.choice("abcXYZ -1") for _ in range(rng.randint(1, 14))))
	if params["rule"] != "pattern":
		return [case(text) for text in texts]
	patterns = ["uul", "u", "l", "lu", "ulll"]
	return [case(text, rng.choice(patterns) if index > 2 else "uul") for index, text in enumerate(texts)]

RULES = {
	"words": ("text: str", "in each word, the letters alternate upper and lower case, starting with\n"
		"an upper case letter: the first letter of each word is in upper case,\n"
		"the second in lower case, and so on. The words are separated by spaces"),
	"pattern": ("text: str, pattern: str", "the letters follow the pattern, a string of u (upper\n"
		"case) and l (lower case) that is never empty. The first letter takes the\n"
		"case of the first character of the pattern, the second letter the case\n"
		"of the second one, and so on, starting the pattern again when it ends"),
	"all_chars": ("text: str", "the character at an even index (0, 2, 4...) is in upper case, the one\n"
		"at an odd index in lower case. Every character counts in the index, but\n"
		"only the letters change"),
}

EXERCISE = Exercise(
	name="case_wave",
	language="python",
	kind="function",
	assignment_name="wave_${rule}",
	expected_files=("wave_${rule}.py",),
	allowed_functions=(),
	themes=("case_alternate",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a function that returns a copy of the string text where\n"
		"$rule.\n"
		"\n"
		"The letters are a to z and A to Z; the other characters stay as they are\n"
		"and, unless said otherwise, are not counted.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("wave_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> str:",
	examples=lambda params: {
		"words": (case("hello big world"), case("it's 42, ok?")),
		"pattern": (case("a-bcd e", "uul"), case("hello", "l")),
		"all_chars": (case("abcd ef"), case("ALL UPPER")),
	}[params["rule"]],
)
