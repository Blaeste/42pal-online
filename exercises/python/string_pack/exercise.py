"""string_pack: an original Python model in the style of "pack a list of
strings into one string and back".

The student writes one side of a given packing: strings ended by ; with
escapes, its reverse, or the reverse of a packing with the length before
each string, with None for what is not right. A packing of the student's
own choice with its reverse, the real subject, is not one of the rules.
"""

import re

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def pack_escape(items):
	return "".join(item.replace("\\", "\\\\").replace(";", "\\;") + ";" for item in items)

def unpack_escape(packed):
	items, current, index = [], "", 0
	while index < len(packed):
		char = packed[index]
		if char == "\\":
			if index + 1 == len(packed) or packed[index + 1] not in "\\;":
				return None
			current += packed[index + 1]
			index += 2
			continue
		if char == ";":
			items.append(current)
			current = ""
		else:
			current += char
		index += 1
	return items if current == "" and not packed.endswith("\\") else None

def unpack_length(packed):
	items, index = [], 0
	while index < len(packed):
		found = re.match(r"\d+:", packed[index:])
		if not found:
			return None
		size = int(found.group()[:-1])
		start = index + len(found.group())
		if start + size > len(packed):
			return None
		items.append(packed[start:start + size])
		index = start + size
	return items

def oracle(params, test):
	(given,) = values(test)
	return shown({"pack_escape": pack_escape, "unpack_escape": unpack_escape,
		"unpack_length": unpack_length}[params["rule"]](given))

def random_items(rng):
	return ["".join(rng.choice("ab;\\:3 ") for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(0, 4))]

def generate_tests(params, rng):
	rule = params["rule"]
	if rule == "pack_escape":
		lists = [[], [""], ["a;b", "c\\"], ["plain"], [";", "\\", ""], ["two words", "3:x"]]
		return [case(items) for items in lists + [random_items(rng) for _ in range(10)]]
	if rule == "unpack_escape":
		texts = ["a\\;b;c\\\\;", "abc", "a\\x;", "", ";;", "a;b", "\\", "x\\\\;", ";"]
		texts += [pack_escape(random_items(rng)) for _ in range(8)]
		texts += [pack_escape(random_items(rng))[:-1] for _ in range(2)]
		return [case(text) for text in texts]
	texts = ["3:abc0:2:de", "3:ab", "x:a", "", "0:", "1:;1::", "10:0123456789", "2:ab3", "-1:a", "01:a"]
	for _ in range(8):
		texts.append("".join(f"{len(item)}:{item}" for item in random_items(rng)))
	return [case(text) for text in texts]

RULES = {
	"pack_escape": ("items: list[str]", "str", "takes a list of strings and returns them packed\n"
		"into one string: each string, followed by a ;. Inside a string, each \\\n"
		"is written \\\\ and each ; is written \\; so that the ; that end the strings\n"
		"can be told apart. The empty list gives an empty string, and a list of\n"
		"one empty string gives ;"),
	"unpack_escape": ("packed: str", "list[str] | None", "takes a string packed this way: each\n"
		"string followed by a ;, where inside a string each \\ is written \\\\ and\n"
		"each ; is written \\; -- and returns the list of the strings. If packed\n"
		"is not right (a \\ followed by anything else than \\ or ;, or characters\n"
		"after the last ;), it returns None. An empty string gives an empty list"),
	"unpack_length": ("packed: str", "list[str] | None", "takes a string packed this way: each\n"
		"string written as its length in decimal, a :, then its characters (3:abc\n"
		"for abc, 0: for an empty string) -- and returns the list of the strings.\n"
		"If packed is not right (no length where one is expected, or fewer\n"
		"characters left than a length says), it returns None. An empty string\n"
		"gives an empty list"),
}

EXERCISE = Exercise(
	name="string_pack",
	language="python",
	kind="function",
	assignment_name="${rule}",
	expected_files=("${rule}.py",),
	allowed_functions=(),
	themes=("string_packing",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that\n"
		"$rule.\n"
		"\n"
		"The strings may hold any character. You may not use eval() nor import\n"
		"anything.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"pack_escape": (case(["a;b", "c\\"]), case([""]), case([])),
		"unpack_escape": (case("a\\;b;c\\\\;"), case(";;"), case("abc")),
		"unpack_length": (case("3:abc0:2:de"), case("3:ab")),
	}[params["rule"]],
)
