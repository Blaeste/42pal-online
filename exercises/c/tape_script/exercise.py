"""tape_script: an original program model in the style of "write a tiny
interpreter".

The program runs a script written in a small language of our own: a tape
of 64 bytes, a current cell, + - > < and a print command, and one kind of
loop per variant: a body repeated the number of times written after it, a
loop that counts the current cell down by itself, or a body repeated as
many times as the value of the cell when the loop starts. The loop of the
real 42 subject, run while the cell is not 0 with no count down, is not one
of them.
"""

from pal42.model import Exercise, Param, TestCase

# The two brackets of the loop of each variant.
BRACKETS = {"times": "()", "countdown": "[]", "repeat": "{}"}

TAPE = 64

class Stuck(Exception):
	"""The script runs too long, or leaves the tape: never one of the tests."""

def closing(script, start, brackets):
	"""The index of the bracket that closes the one at `start`."""
	depth = 0
	for index in range(start, len(script)):
		if script[index] == brackets[0]:
			depth += 1
		elif script[index] == brackets[1]:
			depth -= 1
			if depth == 0:
				return index
	raise Stuck("unbalanced")

class Machine:
	def __init__(self, script, loop, show):
		self.script, self.loop, self.show = script, loop, show
		self.tape, self.at, self.out, self.steps = [0] * TAPE, 0, [], 0

	def run(self, start, end):
		brackets = BRACKETS[self.loop]
		index = start
		while index < end:
			self.steps += 1
			if self.steps > 200_000:
				raise Stuck("too long")
			char = self.script[index]
			if char in "+-":
				self.tape[self.at] = (self.tape[self.at] + (1 if char == "+" else -1)) % 256
			elif char in "<>":
				self.at += 1 if char == ">" else -1
				if not 0 <= self.at < TAPE:
					raise Stuck("off the tape")
			elif char == ".":
				value = self.tape[self.at]
				self.out.append(chr(value) if self.show == "char" else f"{value}\n")
			elif char == brackets[0]:
				close = closing(self.script, index, brackets)
				if self.loop == "times":
					for _ in range(int(self.script[close + 1])):
						self.run(index + 1, close)
					close += 1
				elif self.loop == "countdown":
					if self.tape[self.at]:
						while True:
							self.run(index + 1, close)
							self.tape[self.at] = (self.tape[self.at] - 1) % 256
							if not self.tape[self.at]:
								break
				else:
					for _ in range(self.tape[self.at]):
						self.run(index + 1, close)
				index = close
			index += 1

def execute(script, loop, show):
	machine = Machine(script, loop, show)
	machine.run(0, len(script))
	return "".join(machine.out)

def oracle(params, test):
	"""Return what the program must print for `test`, in the variant `params`."""
	if len(test.args) != 1:
		return "\n"
	return execute(test.args[0], params["loop"], params["print"])

def random_script(rng, loop, depth=0):
	"""A short script: changes, moves, prints and loops, nested twice at most."""
	parts = []
	for _ in range(rng.randint(1, 4)):
		kind = rng.randint(0, 4)
		if kind == 0:
			parts.append("+" * rng.randint(1, 9))
		elif kind == 1:
			parts.append("-" * rng.randint(1, 2))
		elif kind == 2:
			parts.append(rng.choice([">", ">>", "<", ".", ">."]))
		elif depth < 2:
			inner = random_script(rng, loop, depth + 1)
			if loop == "times":
				parts.append(f"({inner}){rng.randint(0, 6)}")
			elif loop == "countdown":
				parts.append(f"[>{inner}<]")
			else:
				parts.append("{>" + inner + "<}")
	return "".join(parts)

def usable(script, loop, show):
	"""Does the script end, stay on the tape and, for char, print plain ASCII?"""
	try:
		out = execute(script, loop, show)
	except Stuck:
		return False
	return show == "number" or all(0 < ord(char) < 128 for char in out)

# Fixed scripts of each loop: the first ones print some text, the others
# show the loop at work (nested, run 0 times, cells that wrap around).
FIXED = {
	"times": ["(+++++++++)8.>((+++++)3)7.", "((++++)4)3++++.--.", "(++++++++)6>+++++(+)5.<.",
		"(+)3.>((++)2)3.", "+(+)0.", "+.x+.y+.", "-.[+]{+}."],
	"countdown": ["++++++++[>+++++++++<]>.+.", "+++++++[>+++++++<]>+++.--.", "+++++[>++<]>.",
		"+++[>++<]>.", "[>+<].", "++[>+++[>+<]<]>>.", "-[>+<]>.", "(+++)[>+<]>."],
	"repeat": ["++++++++{>+++++++++<}>.+.", "+++++++{>+++++++<}>+++.--.", "+++++{>++<}>.",
		"++{>+++{>+<}<}>>.", "+++{>++<}>.", "{>+<}>+.", "(+++)[++]{.}", "-."],
}

def readable(script, loop, show):
	"""Does the script print only plain text (a newline at most)?"""
	return all(char == "\n" or " " <= char <= "~" for char in execute(script, loop, show))

def examples(params):
	"""The first three fixed scripts of the loop whose output is plain text."""
	loop, show = params["loop"], params["print"]
	return tuple(TestCase((script,)) for script in FIXED[loop] if readable(script, loop, show))[:3]

def generate_tests(params, rng):
	"""Return the test cases: fixed scripts first, then random ones that end."""
	loop, show = params["loop"], params["print"]
	tests = [TestCase(()), TestCase(("",)), TestCase(("a", "b"))]
	tests += [TestCase((script,)) for script in FIXED[loop] if usable(script, loop, show)]
	added = 0
	while added < 10:
		script = random_script(rng, loop) + rng.choice([".", ">.", "<."])
		if usable(script, loop, show):
			tests.append(TestCase((script,)))
			added += 1
	return tests

COMMANDS = (
	"\t+\tadds 1 to the current cell (255 + 1 gives 0)\n"
	"\t-\tsubtracts 1 from the current cell (0 - 1 gives 255)\n"
	"\t>\tmakes the next cell the current one\n"
	"\t<\tmakes the previous cell the current one\n"
	"\t.\tdisplays the current cell"
)

EXERCISE = Exercise(
	name="tape_script",
	language="c",
	kind="program",
	assignment_name="tape_${loop}_${print}",
	expected_files=("tape_${loop}_${print}.c",),
	allowed_functions=("write",),
	themes=("tiny_interpreter",),
	params=(
		Param("loop", ("times", "countdown", "repeat"), {
			"times": "( and ), always followed by a digit d from 0 to 9: the commands between\n"
				"the brackets are run d times in a row (not at all for 0), then the script\n"
				"goes on after the digit",
			"countdown": "[ and ]. When the script reaches [, if the current cell is 0, it goes\n"
				"on after the matching ]. When it reaches ], it subtracts 1 from the\n"
				"current cell; then, if the current cell is not 0, it goes back to just\n"
				"after the matching [",
			"repeat": "{ and }. When the script reaches {, the commands between the brackets\n"
				"are run as many times as the value of the current cell at that moment\n"
				"(not at all for 0); the loop itself does not change the cell. Then the\n"
				"script goes on after the matching }",
		}),
		Param("print", ("char", "number"), {
			"char": "as a character (one byte)",
			"number": "as a number in decimal, followed by a newline",
		}),
	),
	subject=(
		"Write a program that takes a script as its only argument and runs it.\n"
		"\n"
		"The script works on a tape of 64 cells of one byte each, all set to 0 at\n"
		"the start. The current cell is the first one at the start. The commands\n"
		"are:\n"
		"\n"
		f"{COMMANDS}\n"
		"\n"
		"The current cell is displayed\n"
		"$print.\n"
		"\n"
		# The hole goes on the same line: a line that starts with { is taken for code.
		"The loops are written with $loop.\n"
		"Loops can be put one inside another.\n"
		"\n"
		"Every other character of the script is ignored. The script is always\n"
		"right: its brackets match, and it never goes off the tape.\n"
		"\n"
		"If the number of arguments is not 1, the program displays a newline."
	),
	oracle=oracle,
	generate_tests=generate_tests,
	examples=examples,
)
