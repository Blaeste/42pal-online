"""say_message: an original program model in the style of "display a fixed message".

The program displays a fixed message, as it is or in uppercase, followed by
a newline. Hello World!, a real 42 subject, is never the message.
"""

from pal42.model import Exercise, Param, TestCase

MESSAGES = {
	"good_morning": "Good morning!",
	"forty_two": "42 is the answer.",
	"see_you": "See you soon!",
}

def oracle(params, test):
	"""Return what the program prints, whatever its arguments."""
	message = MESSAGES[params["message"]]
	return (message.upper() if params["case"] == "upper" else message) + "\n"

def generate_tests(params, rng):
	return [TestCase(()), TestCase(("hello",)), TestCase(("Hello", "World!"))]

EXERCISE = Exercise(
	name="say_message",
	language="c",
	kind="program",
	assignment_name="say_${message}_${case}",
	expected_files=("say_${message}_${case}.c",),
	allowed_functions=("write",),
	themes=("fixed_message",),
	params=(
		Param("message", ("good_morning", "forty_two", "see_you"), {
			"good_morning": "Good morning!",
			"forty_two": "42 is the answer.",
			"see_you": "See you soon!",
		}),
		Param("case", ("as_is", "upper"), {
			"as_is": "written exactly like this",
			"upper": "with its lowercase letters turned into uppercase",
		}),
	),
	subject=(
		"Write a program that displays the message\n"
		"$message\n"
		"$case,\n"
		"followed by a newline.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
