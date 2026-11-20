"""Writing the subject of a variant in the 42 format.

Like the rest of the core, this module never prints: it returns the text,
and the front-ends write it (subject.en.txt in the terminal, a page on the web).
"""

import re
import textwrap
from string import Template

# An argument made only of these characters needs no quotes in a shell.
PLAIN_ARG = re.compile(r"[A-Za-z0-9_./=:,+-]+")

def render(variant):
	"""Return the subject of `variant`, in the 42 format.

	The header, a line of dashes, the statement, then the examples if the
	exercise has some.
	"""
	exo = variant.exercise
	if exo.language == "python":
		# What a Python file may use: modules to import, and calls it may not make.
		allowed = [f"Allowed imports  : {', '.join(exo.allowed_imports) or 'none'}"]
		if exo.forbidden_calls:
			allowed.append(f"Forbidden        : {', '.join(f'{name}()' for name in exo.forbidden_calls)}")
	else:
		allowed = [f"Allowed functions: {', '.join(exo.allowed_functions)}"]
	# The labels are padded so that the colons line up, like in the 42 subjects.
	lines = [
		f"Assignment name  : {variant.name}",
		f"Expected files   : {', '.join(variant.expected_files)}",
		*allowed,
		# Files given by the exercise, next to the subject (a header...).
		*([f"Given files      : {', '.join(exo.provided_files)}"] if exo.provided_files else []),
		"-" * 80,
		"",
		statement(variant),
	]
	if variant.examples:
		lines += ["", "Examples:", ""] + _examples(variant)
	return "\n".join(lines) + "\n"

def statement(variant):
	"""Return the statement of `variant`: each `$param` becomes its text.

	The name and the files use the drawn values (repeat_twice), but the
	statement uses their texts ("2 times"), see Param.texts.
	"""
	texts = {
		param.name: param.text(variant.params[param.name])
		for param in variant.exercise.params
	}
	# $assignment: the name of the program or function, for a prototype.
	texts["assignment"] = variant.name
	# $prototype: a declaration that changes with the variant.
	if variant.exercise.prototype:
		texts["prototype"] = wrap_declaration(variant.exercise.prototype(variant.name, variant.params))
	return reflow(Template(variant.exercise.subject).substitute(texts))

def reflow(text, width=80):
	"""Wrap each paragraph of prose at `width` columns, like the 42 subjects.

	The texts of the params come with their own line breaks: the lines of a
	paragraph are joined, then wrapped again, so that a sentence reads in one
	go. A paragraph of code (a prototype, a header: a line with a tab, or
	starting with a space, #, { or }) stays as it is.
	"""
	paragraphs = []
	for paragraph in text.split("\n\n"):
		lines = paragraph.split("\n")
		if any("\t" in line or line.startswith((" ", "#", "{", "}", "def ", "class ")) for line in lines):
			paragraphs.append(paragraph)
			continue
		# A line that starts with "- " starts an item of a list: each item is
		# wrapped on its own, its next lines under its text.
		parts = [[]]
		for line in lines:
			if line.startswith("- ") and parts[-1]:
				parts.append([])
			parts[-1].append(line.strip())
		paragraphs.append("\n".join(
			textwrap.fill(" ".join(part), width, subsequent_indent="  " if part[0].startswith("- ") else "",
				break_long_words=False, break_on_hyphens=False)
			for part in parts))
	return "\n\n".join(paragraphs)

def wrap_declaration(text, width=79):
	"""A Python declaration longer than `width`: its arguments go on lines of their own.

	def name(
	        argument, argument,
	        argument) -> returned:

	The arguments are cut at their commas only, never inside a type like
	dict[str, list[str]], and put on as few lines as fit.
	"""
	if not text.startswith("def ") or "\n" in text or len(text) <= width:
		return text
	head, rest = text.split("(", 1)
	# The arguments, cut at the commas outside brackets; the last piece keeps ") -> ...:".
	pieces, depth, start = [], 0, 0
	for index, char in enumerate(rest):
		depth += char in "[(" and 1 or char in "])" and -1 or 0
		if char == "," and depth == 0:
			pieces.append(rest[start:index + 1].strip())
			start = index + 1
	pieces.append(rest[start:].strip())
	lines, current = [], ""
	for piece in pieces:
		if current and len("        " + current + " " + piece) > width:
			lines.append(current)
			current = piece
		else:
			current = f"{current} {piece}".strip()
	lines.append(current)
	return f"{head}(\n" + "\n".join("        " + line for line in lines)

def _examples(variant):
	"""Return the lines of the examples: each command, then what it prints.

	The outputs are computed by the oracle for this variant, never by hand.
	"""
	exo = variant.exercise
	lines = []
	for test in variant.examples:
		if exo.language == "python" and exo.call:
			# Like in the Python shell: the call, then what it returns.
			lines.append(f">>> {exo.call(variant.name, test)}")
			lines.append(exo.oracle(variant.params, test).removesuffix("\n"))
			continue
		# A program shows its shell command; a function, its call.
		if exo.call:
			lines.append(exo.call(variant.name, test))
		else:
			lines.append(f"$>{example_command(variant.name, test)} | cat -e")
		# render() joins the lines with \n, so the last one of the output
		# is removed here; an output without \n ends without $, as in cat -e.
		lines.append(cat_e(exo.oracle(variant.params, test)).removesuffix("\n"))
	return lines

def test_command(variant, test):
	"""How a trace shows `test`: the call of a function, or ./name args | cat -e."""
	if variant.exercise.call:
		return variant.exercise.call(variant.name, test)
	return f"{example_command(variant.name, test)} | cat -e"

def example_command(name, test):
	"""Return the command that runs the program `name` on `test`: ./name args."""
	return " ".join([f"./{name}", *map(shell_quote, test.args)])

def shell_quote(arg):
	"""Return `arg` written the way an example shows it in a shell command.

	A plain word stays as it is (hello); anything else gets double quotes,
	like in the 42 subjects ("ab c"). Copied into a shell, the example gives
	the program exactly the same argument.
	"""
	if PLAIN_ARG.fullmatch(arg):
		return arg
	# Inside double quotes, the shell still reads \ " $ and `: a \ in front
	# of each makes it a plain character.
	escaped = re.sub(r'([\\"$`])', r"\\\1", arg)
	return f'"{escaped}"'

def cat_e(text):
	"""Return `text` shown the way `cat -e` does.

	text is a str (an oracle's output) or bytes (a program's output).
	A `$` marks each end of line, so a missing \\n can be seen, and the
	invisible bytes are shown too: ^A for a control character, ^? for DEL,
	and M- in front of a byte above 127.
	"""
	if isinstance(text, str):
		text = text.encode()
	return "".join(_show_byte(byte) for byte in text)

def _show_byte(byte):
	"""One byte (0 to 255) shown the way `cat -e` does."""
	if byte == ord("\n"):
		return "$\n"
	if byte == ord("\t"):
		return "\t"
	# Above 127: "M-", then the byte minus 128 with the same rules,
	# so 128 + 1 gives M-^A and 128 + ord("a") gives M-a.
	if byte >= 128:
		return "M-" + _show_ascii(byte - 128)
	return _show_ascii(byte)

def _show_ascii(byte):
	"""One byte from 0 to 127: control characters get the ^ notation."""
	# Control characters 0 to 31 are shown as ^ and the letter 64 further:
	# 1 gives ^A, 27 (escape) gives ^[.
	if byte < 32:
		return "^" + chr(byte + 64)
	if byte == 127:
		return "^?"
	return chr(byte)

# How C writes the characters that cannot appear as they are in a literal.
C_ESCAPES = {"\\": "\\\\", "\n": "\\n", "\t": "\\t", "\r": "\\r"}

def c_string(text):
	"""Return `text` written as a C string literal: "say \\"hi\\"\\n"."""
	escaped = "".join(C_ESCAPES.get(char, char) for char in text).replace('"', '\\"')
	return f'"{escaped}"'

def c_char(char):
	"""Return one character written as a C character literal: 'a', '\\''."""
	escaped = C_ESCAPES.get(char, char).replace("'", "\\'")
	return f"'{escaped}'"
