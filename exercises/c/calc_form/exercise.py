"""calc_form: an original program model in the style of "a small calculator".

The program takes two numbers and an operation, in infix, prefix or postfix
order, the operation written as a symbol or as a word, and displays the
result alone or the whole equation. Infix order, symbols and the result
alone give back a real 42 subject: it is left out.
"""

from pal42.model import Exercise, Param, TestCase

SYMBOLS = ["+", "-", "*", "/", "%"]
WORDS = ["plus", "minus", "times", "over", "mod"]

def compute(kind, a, b):
	"""a <kind> b, the kind an index in SYMBOLS; / and % go toward zero, like in C."""
	if kind == 0:
		return a + b
	if kind == 1:
		return a - b
	if kind == 2:
		return a * b
	quotient = abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)
	return quotient if kind == 3 else a - b * quotient

def place_of_operator(order):
	"""Where the operation is among the three arguments."""
	return {"infix": 1, "prefix": 0, "postfix": 2}[order]

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 3:
		return "\n"
	args = list(test.args)
	operator = args.pop(place_of_operator(params["order"]))
	a, b = int(args[0]), int(args[1])
	names = SYMBOLS if params["operators"] == "symbols" else WORDS
	result = compute(names.index(operator), a, b)
	if params["show"] == "equation":
		return f"{a} {operator} {b} = {result}\n"
	return f"{result}\n"

def written(params, a, kind, b):
	"""The three arguments for a <kind> b, in the order and words of the variant."""
	operator = (SYMBOLS if params["operators"] == "symbols" else WORDS)[kind]
	args = [str(a), str(b)]
	args.insert(place_of_operator(params["order"]), operator)
	return TestCase(tuple(args))

def generate_tests(params, rng):
	"""Return the test cases: every operation, signs, then random ones."""
	tests = [TestCase(()), TestCase(("1", "2")), TestCase(("1", "2", "3", "4"))]
	for a, kind, b in [(7, 0, 3), (7, 1, 10), (-6, 2, 7), (7, 3, 2), (-7, 3, 2), (-7, 4, 2),
			(7, 4, -3), (0, 2, 99), (2147483647, 1, 1)]:
		tests.append(written(params, a, kind, b))
	for _ in range(8):
		kind = rng.randrange(5)
		b = rng.choice([n for n in range(-50, 51) if n != 0])
		tests.append(written(params, rng.randint(-1000, 1000), kind, b))
	return tests

def examples(params):
	"""The examples of the subject, written in the order and words of the variant."""
	return (written(params, 7, 0, 3), written(params, -7, 3, 2), TestCase(("42",)))

EXERCISE = Exercise(
	name="calc_form",
	language="c",
	kind="program",
	assignment_name="calc_${order}_${operators}_${show}",
	expected_files=("calc_${order}_${operators}_${show}.c",),
	allowed_functions=("write", "atoi"),
	themes=("calculator",),
	params=(
		Param("order", ("infix", "prefix", "postfix"), {
			"infix": "a number, the operation, then a number (7 + 3)",
			"prefix": "the operation, then the two numbers (+ 7 3)",
			"postfix": "the two numbers, then the operation (7 3 +)",
		}),
		Param("operators", ("symbols", "words"), {
			"symbols": "one of the symbols +, -, *, / and %",
			"words": "one of the words plus, minus, times, over and mod (for +, -, *, /\n"
				"and %)",
		}),
		Param("show", ("result", "equation"), {
			"result": "the result alone",
			"equation": "the equation: the first number, the operation as given, the second\n"
				"number, = and the result, separated by spaces (7 + 3 = 10)",
		}),
	),
	# Infix order, symbols, the result alone: a real subject.
	forbidden=({"order": "infix", "operators": "symbols", "show": "result"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that takes three arguments, in this order:\n"
		"$order.\n"
		"The operation is\n"
		"$operators.\n"
		"The program displays\n"
		"$show,\n"
		"followed by a newline.\n"
		"\n"
		"The numbers are ints, written in base 10, maybe with a minus sign; the\n"
		"second one is never 0 for / and %, and every result fits in an int. / and %\n"
		"work like in C: 7 / 2 = 3, -7 / 2 = -3 and -7 % 2 = -1.\n"
		"\n"
		"If the number of arguments is not 3, the program displays only a newline."
	),
	examples=examples,
	oracle=oracle,
	generate_tests=generate_tests,
)
