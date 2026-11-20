"""expr_eval: an original program model in the style of "compute an
expression with a stack".

The program computes an expression written in prefix notation, in compact
postfix notation (one digit per number, no spaces), or as a nested infix
expression with a pair of brackets around each operation. The real 42
subject, postfix with spaces between the tokens, is not one of the
variants.
"""

from pal42.model import Exercise, Param, TestCase

DIGITS = "0123456789"
OPERATORS = "+-*/%"
INT_MAX = 2**31 - 1

class Wrong(Exception):
	"""The expression is wrong, or divides by 0: the program displays Error."""

def checked(value):
	"""A value that fits in an int; the tests never hold a bigger one."""
	if not -INT_MAX - 1 <= value <= INT_MAX:
		raise OverflowError(value)
	return value

def apply(operator, left, right):
	"""left operator right, like C computes it on ints."""
	if operator in "/%" and right == 0:
		raise Wrong
	if operator == "+":
		return checked(left + right)
	if operator == "-":
		return checked(left - right)
	if operator == "*":
		return checked(left * right)
	# C cuts the quotient toward 0; the remainder has the sign of left.
	quotient = abs(left) // abs(right)
	if (left < 0) != (right < 0):
		quotient = -quotient
	return checked(quotient if operator == "/" else left - right * quotient)

def number(token):
	if not token or any(char not in DIGITS for char in token):
		raise Wrong
	return checked(int(token))

def prefix(text):
	"""Read the tokens from the last: a number goes on the stack, an operator takes two."""
	stack = []
	for token in reversed([token for token in text.split(" ") if token]):
		if token in tuple(OPERATORS):
			if len(stack) < 2:
				raise Wrong
			left = stack.pop()
			stack.append(apply(token, left, stack.pop()))
		else:
			stack.append(number(token))
	if len(stack) != 1:
		raise Wrong
	return stack[0]

def compact(text):
	"""Read the characters from the first: a digit goes on the stack, an operator takes two."""
	stack = []
	for char in text:
		if char in OPERATORS:
			if len(stack) < 2:
				raise Wrong
			right = stack.pop()
			stack.append(apply(char, stack.pop(), right))
		else:
			stack.append(number(char))
	if len(stack) != 1:
		raise Wrong
	return stack[0]

def nested(text):
	"""An expression is a number, or ( expression operator expression )."""
	position = 0

	def expression():
		nonlocal position
		if text[position:position + 1] == "(":
			position += 1
			left = expression()
			operator = text[position:position + 1]
			if not operator or operator not in OPERATORS:
				raise Wrong
			position += 1
			right = expression()
			if text[position:position + 1] != ")":
				raise Wrong
			position += 1
			return apply(operator, left, right)
		start = position
		while text[position:position + 1] and text[position] in DIGITS:
			position += 1
		return number(text[start:position])

	value = expression()
	if position != len(text):
		raise Wrong
	return value

NOTATIONS = {"prefix": prefix, "compact": compact, "nested": nested}

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	try:
		return f"{NOTATIONS[params['notation']](test.args[0])}\n"
	except Wrong:
		return "Error\n"

def random_tree(rng, notation, depth=0):
	"""A random expression: a number, or (operator, left, right)."""
	if depth >= 3 or rng.randint(0, 2) == 0:
		return rng.randint(0, 9 if notation == "compact" else 60)
	return (rng.choice("+-*/%" if rng.randint(0, 3) else "+*"),
		random_tree(rng, notation, depth + 1), random_tree(rng, notation, depth + 1))

def written(tree, notation):
	"""The expression `tree` written in `notation`."""
	if isinstance(tree, int):
		return str(tree)
	operator, left, right = tree
	left, right = written(left, notation), written(right, notation)
	if notation == "prefix":
		return f"{operator} {left} {right}"
	if notation == "compact":
		return f"{left}{right}{operator}"
	return f"({left}{operator}{right})"

def spoiled(rng, text):
	"""text with one character removed, doubled or replaced: often wrong."""
	if not text:
		return "+"
	index = rng.randrange(len(text))
	change = rng.randint(0, 2)
	if change == 0:
		return text[:index] + text[index + 1:]
	if change == 1:
		return text[:index] + text[index] + text[index:]
	return text[:index] + rng.choice("+( 7x") + text[index + 1:]

FIXED = {
	"prefix": ["+ 3 4", "* + 1 2 4", "- 2 5", "/ 7 2", "% -7 2", "  /  7 2 ", "42", "% 7 0",
		"+ 3", "3 4", "+ 3 4 5", "", "+3 4", "- * 6 7 / 100 % 17 5"],
	"compact": ["34+2*", "25-", "72/", "9", "05-3/", "05-3%", "70%", "3+", "34", "", "3 4+", "12",
		"93-4*82/+"],
	"nested": ["((3+4)*2)", "(2-5)", "((10/3)*3)", "42", "3+4", "((3+4)", "(3+4))", "(7%0)", "()",
		"(3 + 4)", "(3+)", "((6*7)-((100/17)%5))"],
}

def generate_tests(params, rng):
	"""Return the test cases: fixed expressions first, then random ones, right or spoiled."""
	notation = params["notation"]
	tests = [TestCase(()), TestCase(("1", "2"))]
	tests += [TestCase((text,)) for text in FIXED[notation]]
	while len(tests) < len(FIXED[notation]) + 14:
		text = written(random_tree(rng, notation), notation)
		if rng.randint(0, 2) == 0:
			text = spoiled(rng, text)
		try:
			oracle(params, TestCase((text,)))
		except OverflowError:
			continue
		tests.append(TestCase((text,)))
	return tests

EXERCISE = Exercise(
	name="expr_eval",
	language="c",
	kind="program",
	assignment_name="expr_${notation}",
	expected_files=("expr_${notation}.c",),
	allowed_functions=("write",),
	themes=("postfix_calc",),
	params=(
		Param("notation", ("prefix", "compact", "nested"), {
			"prefix": "in prefix notation: each operator comes before its two operands, and\n"
				"the numbers and operators are separated by one space or more (there may\n"
				"be spaces at the start and at the end too). For example, - * 6 7 2 is\n"
				"(6 * 7) - 2",
			"compact": "in compact postfix notation: each operator comes after its two\n"
				"operands, each number is one digit, and there are no spaces. For\n"
				"example, 67*2- is (6 * 7) - 2",
			"nested": "with brackets: an expression is a number, or ( then an expression, an\n"
				"operator, an expression, then ), with no spaces. For example,\n"
				"((6*7)-2) is (6 * 7) - 2",
		}),
	),
	subject=(
		"Write a program that takes an expression as its only argument, and\n"
		"displays its value followed by a newline. The expression is written\n"
		"$notation.\n"
		"\n"
		"The numbers are made of digits only, and the operators are + - * / and %,\n"
		"computed on ints like in C. Each expression has at most 1000 characters,\n"
		"and the numbers, the value and the values along the way all fit in an int.\n"
		"\n"
		"If the expression is not written right (an unknown character, an operator\n"
		"that lacks an operand, a number left over...) or divides by 0 (with / or\n"
		"%), the program displays Error followed by a newline.\n"
		"\n"
		"If the number of arguments is not 1, the program displays a newline."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	examples=lambda params: tuple(TestCase((text,)) for text in {
		"prefix": ("* + 1 2 4", "- * 6 7 / 100 % 17 5", "% 7 0", "+ 3"),
		"compact": ("34+2*", "93-4*82/+", "70%", "3+"),
		"nested": ("((3+4)*2)", "((6*7)-((100/17)%5))", "(7%0)", "3+4"),
	}[params["notation"]]),
)
