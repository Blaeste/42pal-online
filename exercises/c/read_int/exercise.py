"""read_int: an original function model in the style of "turn a string into an int".

The student writes a function that reads an int written in base 10, with
its own rules for what may come before it (spaces, nothing, or anything)
and for its signs (one, many, or a minus only). The rules of atoi (spaces,
then one sign) are a real 42 subject, and spaces then many signs are a
piscine exercise: both are left out.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

SPACES = " \t\n\v\f\r"

def read_sign(text, i, signs):
	"""The sign at text[i] and the index after it (1 and i when there is none)."""
	if signs == "one" and i < len(text) and text[i] in "+-":
		return (-1 if text[i] == "-" else 1), i + 1
	if signs == "minus_only" and i < len(text) and text[i] == "-":
		return -1, i + 1
	sign = 1
	if signs == "many":
		while i < len(text) and text[i] in "+-":
			sign = -sign if text[i] == "-" else sign
			i += 1
	return sign, i

def starts_number(text, i, signs):
	"""True if a number (its signs, then a digit) starts at text[i]."""
	_, after = read_sign(text, i, signs)
	return after < len(text) and "0" <= text[after] <= "9"

def read(text, start, signs):
	"""The int that `text` starts with, by the rules of the variant."""
	i = 0
	if start == "spaces":
		while i < len(text) and text[i] in SPACES:
			i += 1
	elif start == "anything":
		while i < len(text) and not starts_number(text, i, signs):
			i += 1
	sign, i = read_sign(text, i, signs)
	value = 0
	while i < len(text) and "0" <= text[i] <= "9":
		value = value * 10 + int(text[i])
		i += 1
	return sign * value

def oracle(params, test):
	"""Return what the test main prints: the int returned, then a newline."""
	return f"{read(test.args[0], params['start'], params['signs'])}\n"

def generate_tests(params, rng):
	"""Return the test cases: fixed strings, then random ones."""
	texts = ["", "42abc", " 42", "-17", "+5", "--5", "+-3", "  \t-12x", " +12", "abc-12def",
		"a+-5", "x+-+-7", "-+-+-3", "a+5", "no digit", "2147483647", "-2147483647", "0"]
	for _ in range(8):
		texts.append("".join(rng.choice(" \tab+-0123456789") for _ in range(rng.randint(1, 10))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; it prints the int returned.
HARNESS = """#include <stdio.h>

int	ft_read_int_${start}_${signs}(char *str);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\\n", ft_read_int_${start}_${signs}(av[1]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="read_int",
	language="c",
	kind="function",
	assignment_name="ft_read_int_${start}_${signs}",
	expected_files=("ft_read_int_${start}_${signs}.c",),
	allowed_functions=(),
	themes=("read_number",),
	params=(
		Param("start", ("spaces", "nothing", "anything"), {
			"spaces": "Before the number, any number of spaces may come (space, \\t, \\n, \\v,\n"
				"\\f and \\r)",
			"nothing": "The number starts at the first character: nothing may come before it",
			"anything": "Any characters may come before the number: the first number of the\n"
				"string is read (its signs, then its first digit)",
		}),
		Param("signs", ("one", "many", "minus_only"), {
			"one": "The digits may come after one sign, + or -",
			"many": "The digits may come after any number of + and -, each - changing the\n"
				"sign",
			"minus_only": "The digits may come after one -; a + is not a sign",
		}),
	),
	# atoi itself, and the piscine's exercise with many signs.
	forbidden=({"start": "spaces", "signs": "one"}, {"start": "spaces", "signs": "many"}),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that returns the int written in base 10 at the start of\n"
		"the string str.\n"
		"$start.\n"
		"$signs.\n"
		"The digits are read up to the first character that is not a digit. If\n"
		"there is no number where it must be, the function returns 0. The number\n"
		"read is always between -2147483647 and 2147483647.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(TestCase(("abc-12def",)), TestCase(("  +-42x",)), TestCase(("x",))),
)
