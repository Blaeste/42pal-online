"""number_read: an original function model on the theme "turn a string into an int".

The student writes a function that reads a whole string as a number in
binary, octal, base 10 or hexadecimal: plain digits, digits after a prefix
(0b, 0o, 0x), or digits in groups cut by underscores (1_000_000). Unlike
atoi, the whole string must be the number, with an optional minus sign:
anything else gives 0.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

RADIX = {"binary": 2, "octal": 8, "decimal": 10, "hex": 16}
DIGITS = {
	"binary": "01",
	"octal": "01234567",
	"decimal": "0123456789",
	"hex": "0123456789abcdefABCDEF",
}
PREFIX = {"binary": "0b", "octal": "0o", "hex": "0x"}
# The letter of Python's format() for each base.
LETTER = {"binary": "b", "octal": "o", "decimal": "d", "hex": "x"}
# The first character that is not a digit of each base.
NOT_A_DIGIT = {"binary": "2", "octal": "8", "decimal": "a", "hex": "g"}

def read(params, text):
	"""The int that `text` is in the variant, or 0 if it is not a whole number."""
	base, form = params["base"], params["format"]
	sign = 1
	if text.startswith("-"):
		sign, text = -1, text[1:]
	if form == "prefixed":
		if not text.startswith(PREFIX[base]):
			return 0
		text = text[2:]
	if form == "grouped":
		groups = text.split("_")
		# An empty group: an underscore at an end, or two in a row.
		if any(not group for group in groups):
			return 0
		text = "".join(groups)
	if not text or any(char not in DIGITS[base] for char in text):
		return 0
	return sign * int(text, RADIX[base])

def oracle(params, test):
	"""Return what the test main prints: the int returned, then a newline."""
	return f"{read(params, test.args[0])}\n"

def written(params, number, group=4, upper=()):
	"""`number` written as the variant reads it: groups of `group` digits from the right.

	upper holds the places of the hexadecimal digits written in uppercase.
	"""
	digits = format(abs(number), LETTER[params["base"]])
	digits = "".join(c.upper() if i in upper else c for i, c in enumerate(digits))
	if params["format"] == "grouped":
		first = len(digits) % group or group
		parts = [digits[:first]] + [digits[i:i + group] for i in range(first, len(digits), group)]
		digits = "_".join(parts)
	if params["format"] == "prefixed":
		digits = PREFIX[params["base"]] + digits
	return ("-" if number < 0 else "") + digits

def generate_tests(params, rng):
	"""Return the test cases: whole numbers and broken ones, then random numbers."""
	texts = [written(params, number) for number in (0, 1, -1, 2147483647, -2147483647, 255)]
	good = written(params, 1234)
	texts += ["", "-", " " + good, good + " ", "+" + good, good + NOT_A_DIGIT[params["base"]]]
	if params["format"] == "prefixed":
		texts += [PREFIX[params["base"]], good[2:], PREFIX[params["base"]] + "-1"]
	if params["format"] == "grouped":
		texts += ["_" + good, good + "_", good.replace("_", "__", 1) if "_" in good else good + "__1"]
	for _ in range(8):
		number = rng.randint(-2**31 + 1, 2**31 - 1)
		upper = {i for i in range(10) if rng.randint(0, 1)}
		texts.append(written(params, number, rng.randint(1, 4), upper))
	return [TestCase((text,)) for text in texts]

def examples(params):
	"""The examples of the subject: two numbers written as the variant reads them, one wrong."""
	return (
		TestCase((written(params, 42),)),
		TestCase((written(params, -1000000, 3),)),
		TestCase(("+" + written(params, 42),)),
	)

# The test main: av[1] is the string; it prints the int returned.
HARNESS = """#include <stdio.h>

int	ft_read_${base}_${format}(char *str);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\\n", ft_read_${base}_${format}(av[1]));
	return (0);
}
"""

EXERCISE = Exercise(
	name="number_read",
	language="c",
	kind="function",
	assignment_name="ft_read_${base}_${format}",
	expected_files=("ft_read_${base}_${format}.c",),
	allowed_functions=(),
	themes=("read_base_number",),
	params=(
		Param("base", ("binary", "octal", "decimal", "hex"), {
			"binary": "in binary (base 2: the digits 0 and 1)",
			"octal": "in octal (base 8: the digits 0 to 7)",
			"decimal": "in base 10 (the digits 0 to 9)",
			"hex": "in hexadecimal (base 16: the digits 0 to 9, then a to f or A to F)",
		}),
		Param("format", ("plain", "prefixed", "grouped"), {
			"plain": "The digits come right after the sign, if any",
			"prefixed": "The digits come after a prefix, right after the sign if any: 0b,\n"
				"0o or 0x for bases 2, 8 and 16, written in lowercase",
			"grouped": "The digits may be cut into groups by underscores, one between two\n"
				"digits, like 1_000_000",
		}),
	),
	# Base 10 has no prefix.
	forbidden=({"base": "decimal", "format": "prefixed"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that reads the string str as a number written\n"
		"$base,\n"
		"and returns its value as an int.\n"
		"\n"
		"The number may start with one minus sign, for a negative number.\n"
		"$format.\n"
		"The whole string must be the number: if anything else is in it (a space,\n"
		"a plus sign, a character that is not a digit of the base...), or if it has\n"
		"no digit, the function returns 0. The number is always between\n"
		"-2147483647 and 2147483647.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"int\t$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=examples,
)
