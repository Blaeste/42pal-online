"""alpha_wave: an original program model in the style of "display the alphabet in alternating case".

The program displays the alphabet, its case changing in waves of 1, 2 or 3
letters, the first wave in lowercase or in uppercase, joined or spaced.
Waves of 1 letter, the first in lowercase, joined, give back a real 42
subject: it is left out.
"""

from pal42.model import Exercise, Param, TestCase

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def oracle(params, test):
	"""Return what the program prints: the alphabet in waves, then a newline."""
	wave = int(params["wave"])
	letters = []
	for index, letter in enumerate(ALPHABET):
		# Wave 0 has the case of start, wave 1 the other one, and so on.
		upper = (index // wave) % 2 == (0 if params["start"] == "upper" else 1)
		letters.append(letter.upper() if upper else letter)
	return (" " if params["separator"] == "spaced" else "").join(letters) + "\n"

def generate_tests(params, rng):
	"""Return the test cases: no argument, then arguments that change nothing."""
	return [TestCase(()), TestCase(("hello",)), TestCase(("a", "b", "c"))]

EXERCISE = Exercise(
	name="alpha_wave",
	language="c",
	kind="program",
	assignment_name="alpha_wave_${wave}_${start}_${separator}",
	expected_files=("alpha_wave_${wave}_${start}_${separator}.c",),
	allowed_functions=("write",),
	themes=("alternating_alphabet",),
	params=(
		Param("wave", ("1", "2", "3"), {
			"1": "every letter",
			"2": "every 2 letters",
			"3": "every 3 letters",
		}),
		Param("start", ("lower", "upper"), {
			"lower": "The first letters are in lowercase",
			"upper": "The first letters are in uppercase",
		}),
		Param("separator", ("joined", "spaced"), {
			"joined": "The letters are joined, with nothing between them",
			"spaced": "The letters are separated by one space",
		}),
	),
	# One letter out of two in uppercase, lowercase first, joined: a real subject.
	forbidden=({"wave": "1", "start": "lower", "separator": "joined"},),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a program that displays the 26 letters of the alphabet, from a to z,\n"
		"followed by a newline. The case of the letters changes\n"
		"$wave.\n"
		"$start.\n"
		"$separator.\n"
		"\n"
		"The program ignores its arguments."
	),
	examples=(TestCase(()),),
	oracle=oracle,
	generate_tests=generate_tests,
)
