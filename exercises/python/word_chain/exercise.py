"""word_chain: an original Python model in the style of "find the shortest
chain of words with a breadth-first search".

The student writes a function that links words that differ by one letter:
the shortest chain itself, how many words can be reached, or the shortest
chain when a step may also add or remove a letter. The length of the
shortest chain of one-letter changes, the real subject, is not one of the
rules.
"""

from collections import deque

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def one_change(a, b):
	return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1

def one_edit(a, b):
	if one_change(a, b):
		return True
	short, long = sorted((a, b), key=len)
	return len(long) == len(short) + 1 and any(long[:i] + long[i + 1:] == short for i in range(len(long)))

def search(start, words, step):
	"""Breadth-first search from start, the words tried in their order: the parent of each word."""
	parent, queue = {start: None}, deque([start])
	while queue:
		word = queue.popleft()
		for other in words:
			if other not in parent and step(word, other):
				parent[other] = word
				queue.append(other)
	return parent

def chain(start, end, words, step):
	parent = search(start, words, step)
	if end not in parent:
		return None
	found = [end]
	while parent[found[-1]] is not None:
		found.append(parent[found[-1]])
	return found[::-1]

def oracle(params, test):
	rule = params["rule"]
	if rule == "reachable":
		start, words = values(test)
		return shown(len(set(search(start, words, one_change)) - {start}))
	start, end, words = values(test)
	if rule == "path":
		return shown(chain(start, end, words, one_change) if end in words or end == start else None)
	found = chain(start, end, words, one_edit) if end in words or end == start else None
	return shown(len(found) if found else 0)

def generate_tests(params, rng):
	words = ["hot", "dot", "dog", "lot", "log", "cog"]
	rule = params["rule"]
	pool = ["cat", "cot", "cog", "dog", "dot", "hat", "hot", "ca", "at", "a", "cart", "coat", "co"]
	if rule == "reachable":
		tests = [case("hit", words), case("hit", []), case("abc", ["abd", "xyz", "abd"]), case("cat", pool)]
		tests += [case(rng.choice(pool), rng.sample(pool, rng.randint(1, 8))) for _ in range(10)]
		return tests
	fixed = [("hit", "cog", words), ("hit", "cog", ["hot"]), ("a", "abc", ["ab", "abc", "b"]),
		("cat", "cot", ["cot"]), ("cat", "dog", ["dog"]), ("same", "same", []), ("cat", "dog", pool)]
	tests = [case(*triple) for triple in fixed]
	for _ in range(10):
		chosen = rng.sample(pool, rng.randint(2, 8))
		tests.append(case(rng.choice(pool), rng.choice(chosen), chosen))
	return tests

RULES = {
	"path": ("start: str, end: str, words: list[str]", "list[str] | None", "returns the shortest\n"
		"chain from start to end: the list of its words, from start to end, each\n"
		"one differing from the one before by one letter changed (None if there\n"
		"is no chain). When several chains are as short, the chain is the one\n"
		"this breadth-first search finds:\n"
		"- it starts from start;\n"
		"- it takes the words reached, in the order they were reached, and from\n"
		"each one, every word of the list one change away and not reached yet, in\n"
		"the order of the list;\n"
		"- each word keeps the word it was first reached from: the chain goes back\n"
		"from end along these words"),
	"reachable": ("start: str, words: list[str]", "int", "returns how many different words of\n"
		"the list (start left out) can be reached from start by changing one\n"
		"letter at a time"),
	"grow": ("start: str, end: str, words: list[str]", "int", "returns the number of words of\n"
		"the shortest chain from start to end, start and end included, where each\n"
		"word comes from the one before by changing one letter, or by adding or\n"
		"removing one letter anywhere; 0 if there is no chain"),
}

EXERCISE = Exercise(
	name="word_chain",
	language="python",
	kind="function",
	assignment_name="chain_${rule}",
	expected_files=("chain_${rule}.py",),
	allowed_functions=(),
	themes=("word_steps",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that links words. Every word of a chain after start must\n"
		"be in the list words; the case matters. The function\n"
		"$rule.\n"
		"\n"
		"A chain from a word to itself is that word alone.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("chain_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"path": (case("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]), case("hit", "cog", ["hot"])),
		"reachable": (case("hit", ["hot", "dot", "dog", "lot", "log", "cog"]),),
		"grow": (case("a", "abc", ["ab", "abc", "b"]), case("cat", "dog", ["dog"])),
	}[params["rule"]],
)
