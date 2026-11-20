"""print_range: an original model on the theme "print fixed characters".

The student writes a void function that displays a range of characters:
the digits, the lowercase or the uppercase letters, up or down, every one
or one out of two. All the digits, up or down, give back two real exam
subjects of this theme: forbidden.
"""

import string

from pal42.model import Exercise, Param, TestCase

# The characters of each range, in increasing order.
RANGES = {
	"digits": string.digits,
	"lowercase": string.ascii_lowercase,
	"uppercase": string.ascii_uppercase,
}

def oracle(params, test):
	"""Return what the function prints: the range, with no newline."""
	chars = RANGES[params["chars"]]
	if params["order"] == "down":
		chars = chars[::-1]
	if params["step"] == "skip":
		chars = chars[::2]
	return chars

def generate_tests(params, rng):
	"""A function with no argument prints always the same: one test is enough."""
	return [TestCase()]

# The test main only calls the function: what it prints is the whole output.
HARNESS = """void	ft_print_${chars}_${order}_${step}(void);

int	main(void)
{
	ft_print_${chars}_${order}_${step}();
	return (0);
}
"""

EXERCISE = Exercise(
	name="print_range",
	language="c",
	kind="function",
	assignment_name="ft_print_${chars}_${order}_${step}",
	expected_files=("ft_print_${chars}_${order}_${step}.c",),
	allowed_functions=("write",),
	themes=("print_digits",),
	params=(
		Param("chars", ("digits", "lowercase", "uppercase"), {
			"digits": "the digits (0 to 9)",
			"lowercase": "the lowercase letters (a to z)",
			"uppercase": "the uppercase letters (A to Z)",
		}),
		Param("order", ("up", "down"), {
			"up": "in increasing order",
			"down": "in decreasing order",
		}),
		Param("step", ("all", "skip"), {
			"all": "every one of them",
			"skip": "one out of two, starting with the first one",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that displays on the standard output\n"
		"$chars,\n"
		"$order,\n"
		"taking $step.\n"
		"It displays nothing else: no newline at the end.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"void\t$assignment(void);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}()",
	examples=(TestCase(),),
	# All the digits, up or down: two real exam subjects.
	forbidden=(
		{"chars": "digits", "order": "up", "step": "all"},
		{"chars": "digits", "order": "down", "step": "all"},
	),
)
