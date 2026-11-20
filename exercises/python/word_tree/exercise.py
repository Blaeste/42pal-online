"""word_tree: an original Python model in the style of "write a class that
stores words in a prefix tree".

The student writes a class WordTree that stores words and answers: how many
words start with a prefix (and removes words), the longest word that starts
a text, or whether a word matches a pattern with dots. The exact search and
the prefix test of the real subject are not one of the rules.
"""

from pal42.model import Exercise, Param
from pal42.python_exercise import class_call, class_case, class_harness, class_values, shown

def run(rule, steps):
	words, results = [], []
	for method, *args in steps:
		if method == "add":
			words.append(args[0])
			results.append(None)
		elif method == "count":
			results.append(sum(1 for word in words if word.startswith(args[0])))
		elif method == "remove":
			results.append(args[0] in words)
			if args[0] in words:
				words.remove(args[0])
		elif method == "longest":
			results.append(max((word for word in words if args[0].startswith(word)), key=len, default=""))
		else:
			pattern = args[0]
			results.append(any(len(word) == len(pattern) and all(p in (".", c) for p, c in zip(pattern, word))
				for word in words))
	return results

def oracle(params, test):
	_, steps = class_values(test)
	return shown(run(params["rule"], steps))

QUESTIONS = {"count": ("count", "remove"), "longest": ("longest",), "pattern": ("match",)}

def random_steps(rng, rule):
	letters = "abc"
	steps = []
	for _ in range(rng.randint(3, 12)):
		if rng.randint(0, 2) == 0:
			steps.append(["add", "".join(rng.choice(letters) for _ in range(rng.randint(1, 4)))])
			continue
		# A prefix to count may be empty; the other questions take a word.
		word = "".join(rng.choice(letters) for _ in range(rng.randint(0 if rule == "count" else 1, 4)))
		question = rng.choice(QUESTIONS[rule])
		if question == "match":
			word = "".join(char if rng.randint(0, 2) else "." for char in word)
		elif question == "longest":
			word += "".join(rng.choice(letters) for _ in range(rng.randint(0, 3)))
		steps.append([question, word])
	return steps

FIXED = {
	"count": [[["add", "car"], ["add", "cat"], ["add", "car"], ["count", "ca"], ["count", "car"],
		["remove", "car"], ["count", "car"], ["remove", "dog"], ["count", ""]], [["count", "a"], ["remove", "a"]]],
	"longest": [[["add", "a"], ["add", "app"], ["add", "apple"], ["longest", "applesauce"],
		["longest", "apricot"], ["longest", "banana"]], [["longest", "x"], ["add", "x"], ["longest", "x"]]],
	"pattern": [[["add", "bad"], ["add", "dad"], ["match", "b.d"], ["match", ".a."], ["match", "...."],
		["match", "c.d"]], [["match", "."], ["add", "z"], ["match", "."]]],
}

def generate_tests(params, rng):
	rule = params["rule"]
	steps = FIXED[rule] + [random_steps(rng, rule) for _ in range(10)]
	return [class_case([], one) for one in steps]

RULES = {
	"count": ("    def count(self, prefix: str) -> int:\n    def remove(self, word: str) -> bool:",
		"- count(prefix) returns how many words added start with prefix (a word\n"
		"added twice counts twice, and every word starts with the empty prefix);\n"
		"- remove(word) takes one copy of word out of the tree and returns True, or\n"
		"returns False if word is not in it."),
	"longest": ("    def longest(self, text: str) -> str:", "- longest(text) returns the longest word\n"
		"added that starts text (text itself counts), or an empty string if there\n"
		"is none."),
	"pattern": ("    def match(self, pattern: str) -> bool:", "- match(pattern) returns True if a word\n"
		"added has as many letters as pattern and matches it: each dot of the\n"
		"pattern stands for any one letter, every other letter must be the same;\n"
		"it returns False otherwise."),
}

EXERCISE = Exercise(
	name="word_tree",
	language="python",
	kind="function",
	assignment_name="tree_${rule}",
	expected_files=("tree_${rule}.py",),
	allowed_functions=(),
	themes=("prefix_tree",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, text) in RULES.items()}),),
	subject=(
		"Write a class named WordTree that stores words in a prefix tree: each node\n"
		"holds the letters that can follow, so that the words that start the same\n"
		"way share their first nodes. The words are made of lowercase letters. Its\n"
		"methods:\n"
		"- WordTree() makes an empty tree;\n"
		"- add(word) puts word in the tree, and returns None;\n"
		"$rule\n"
		"\n"
		"The methods return their results and print nothing.\n"
		"\n"
		"Your class must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=class_harness("tree_${rule}", "WordTree"),
	call=class_call("WordTree"),
	prototype=lambda name, params: ("class WordTree:\n    def __init__(self) -> None:\n"
		"    def add(self, word: str) -> None:\n" + RULES[params["rule"]][0]),
	examples=lambda params: {
		"count": (class_case([], [["add", "car"], ["add", "cat"], ["add", "car"], ["count", "ca"]]),
			class_case([], [["add", "ab"], ["remove", "ab"], ["remove", "ab"], ["count", "a"]])),
		"longest": (class_case([], [["add", "a"], ["add", "apple"], ["longest", "applesauce"]]),
			class_case([], [["add", "app"], ["longest", "ap"]])),
		"pattern": (class_case([], [["add", "bad"], ["add", "dad"], ["match", ".a."], ["match", "c.d"]]),),
	}[params["rule"]],
)
