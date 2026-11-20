"""base_shift: an original Python model in the style of "read and write
numbers in a base from 2 to 36".

The student writes a function that takes a number written in a string and
a base: it gives the number in decimal, writes a decimal number in the
base, or gives the next number in the same base, with None for what is not
right. Converting from one base to another base, the real subject, is not
one of the operations.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def read(number, base):
	"""The value of number written in base, or None if it is not right."""
	if not 2 <= base <= 36:
		return None
	negative = number.startswith("-")
	body = number[1:] if negative else number
	if not body or any(char.upper() not in DIGITS[:base] for char in body):
		return None
	value = int(body, base)
	return -value if negative else value

def write(value, base):
	digits = ""
	rest = abs(value)
	while True:
		digits = DIGITS[rest % base] + digits
		rest //= base
		if not rest:
			break
	return "-" + digits if value < 0 else digits

def oracle(params, test):
	number, base = values(test)
	op = params["op"]
	if op == "from_decimal":
		value = read(number, 10) if 2 <= base <= 36 else None
		return shown(None if value is None else write(value, base))
	value = read(number, base)
	if value is None:
		return shown(None)
	return shown(str(value) if op == "to_decimal" else write(value + 1, base))

def generate_tests(params, rng):
	pairs = [("ff", 16), ("-101", 2), ("12", 2), ("1", 37), ("255", 16), ("-5", 2), ("0", 36),
		("1a", 16), ("FF", 16), ("-10", 2), ("-1", 7), ("", 10), ("-", 10), ("zz", 36), ("+1", 10),
		("007", 8), ("1", 1), ("-0", 3), ("1 0", 10)]
	for _ in range(8):
		base = rng.randint(2, 36)
		value = rng.randint(-5000, 5000)
		if params["op"] == "from_decimal":
			pairs.append((str(value), base))
		else:
			number = write(value, base)
			pairs.append((number.lower() if rng.randint(0, 1) else number, base))
	return [case(number, base) for number, base in pairs]

EXERCISE = Exercise(
	name="base_shift",
	language="python",
	kind="function",
	assignment_name="base_${op}",
	expected_files=("base_${op}.py",),
	allowed_functions=(),
	themes=("base_convert",),
	params=(
		Param("op", ("to_decimal", "from_decimal", "next"), {
			"to_decimal": "the value of the number, written in that base, as a string written in\n"
				"decimal",
			"from_decimal": "the value of the number, written in decimal, as a string written in\n"
				"that base",
			"next": "the number that follows it (the number plus one), as a string written\n"
				"in that base too",
		}),
	),
	subject=(
		"Write a function that takes a number written in a string and a base from 2\n"
		"to 36, and returns\n"
		"$op.\n"
		"\n"
		"The digits of a base go from 0 to 9, then from A to Z for 10 to 35: a base\n"
		"uses the first ones only (0 and 1 for base 2). Letters are read in either\n"
		"case and written in upper case. A number may start with a - sign; nothing\n"
		"else but its digits may be in it. The result has no zeros in front.\n"
		"\n"
		"The function returns None if the base is not from 2 to 36, or if the number\n"
		"has no digit or holds a character that is not one of its digits.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"def $assignment(number: str, base: int) -> str | None:"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("base_${op}"),
	call=call,
	examples=lambda params: {
		"to_decimal": (case("ff", 16), case("-101", 2), case("12", 2)),
		"from_decimal": (case("255", 16), case("-5", 2), case("1a", 16)),
		"next": (case("FF", 16), case("-10", 2), case("", 10)),
	}[params["op"]],
)
