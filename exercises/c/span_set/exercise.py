"""span_set: an original function model in the style of "measure the start of a string".

The student writes a function that returns how many characters of a set
(digits, letters, blanks or vowels) there are in a row at the start or at
the end of a string. The real 42 subject takes the set as an argument and
counts the characters out of it.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

SETS = {
	"digits": "0123456789",
	"letters": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"blanks": " \t",
	"vowels": "aeiouAEIOU",
}

def oracle(params, test):
	"""Return what the test main prints: the size returned, then a newline."""
	text = test.args[0]
	if params["side"] == "end":
		text = text[::-1]
	count = 0
	while count < len(text) and text[count] in SETS[params["set"]]:
		count += 1
	return f"{count}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed strings, then random ones."""
	texts = ["", "123abc45", "abC12", "ab \t ", "aEiXy", "x12", "2024", " \t ", "Oui! 42 eau"]
	for _ in range(8):
		texts.append("".join(rng.choice("aeBx 1\t9") for _ in range(rng.randint(1, 12))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; it prints the size returned.
HARNESS = """#include <stdio.h>
#include <stddef.h>

size_t	ft_span_${set}_${side}(char *s);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%zu\\n", ft_span_${set}_${side}(av[1]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="span_set",
	language="c",
	kind="function",
	assignment_name="ft_span_${set}_${side}",
	expected_files=("ft_span_${set}_${side}.c",),
	allowed_functions=(),
	themes=("char_span",),
	params=(
		Param("set", ("digits", "letters", "blanks", "vowels"), {
			"digits": "digits (0 to 9)",
			"letters": "letters (a to z and A to Z)",
			"blanks": "blanks (spaces and tabs)",
			"vowels": "vowels (a, e, i, o, u, in either case)",
		}),
		Param("side", ("start", "end"), {
			"start": "at the start of s: from its first character, up to the first one that\n"
				"is not in the set",
			"end": "at the end of s: from its last character back, up to the first one that\n"
				"is not in the set",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns how many\n"
		"$set\n"
		"there are in a row\n"
		"$side.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"size_t\t$assignment(char *s);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("123abc45",)), TestCase(("Oui! 42 eau",)), TestCase(("",))),
)
