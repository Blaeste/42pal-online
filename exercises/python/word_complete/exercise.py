"""word_complete: an original Python model in the style of "complete words
from a prefix".

The student writes a function that completes words: the k most frequent
words that start with a prefix, the letters that can come after a prefix,
or the shortest prefix that tells each word apart. Every word that starts
with a prefix in alphabetical order, the real subject, is not one of the
rules.
"""

from collections import Counter

from pal42.model import Exercise, Param
from pal42.python_exercise import call, case, harness, shown, values

def oracle(params, test):
	rule = params["rule"]
	if rule == "top_k":
		words, prefix, k = values(test)
		counts = Counter(word for word in words if word.startswith(prefix))
		return shown(sorted(counts, key=lambda word: (-counts[word], word))[:k])
	if rule == "next_letters":
		words, prefix = values(test)
		return shown("".join(sorted({word[len(prefix)] for word in words
			if word.startswith(prefix) and len(word) > len(prefix)})))
	(words,) = values(test)
	result = []
	for word in words:
		others = [other for other in words if other != word]
		result.append(next((word[:size] for size in range(1, len(word) + 1)
			if not any(other.startswith(word[:size]) for other in others)), word))
	return shown(result)

POOL = ["car", "cat", "cart", "care", "dog", "do", "dot", "cab", "a", "Cat"]

def generate_tests(params, rng):
	rule = params["rule"]
	words = ["car", "cat", "car", "cart", "dog", "cat", "car"]
	if rule == "top_k":
		tests = [case(words, "ca", 2), case(words, "", 10), case(words, "x", 3), case(words, "car", 0),
			case(["b", "a", "b", "a"], "", 1)]
		tests += [case([rng.choice(POOL) for _ in range(rng.randint(0, 9))], rng.choice(["", "c", "ca", "d"]),
			rng.randint(0, 4)) for _ in range(10)]
		return tests
	if rule == "next_letters":
		tests = [case(["car", "cat", "cart", "ca", "dog"], "ca"), case(words, ""), case(words, "zz"),
			case(["Cat", "cat"], "")]
		tests += [case(rng.sample(POOL, rng.randint(0, 6)), rng.choice(["", "c", "ca", "d", "car"]))
			for _ in range(10)]
		return tests
	tests = [case(["dog", "cat", "car", "cart"]), case([]), case(["solo"]), case(["a", "ab", "abc"])]
	tests += [case(rng.sample(POOL, rng.randint(1, 7))) for _ in range(10)]
	return tests

RULES = {
	"top_k": ("words: list[str], prefix: str, k: int", "list[str]", "takes a list of words, where\n"
		"a word may appear several times, a prefix and an int k from 0. Among the\n"
		"words that start with prefix, it returns the k found the most times in\n"
		"the list, each once (fewer if there are fewer): the most frequent first,\n"
		"and in ASCII order among words found as many times"),
	"next_letters": ("words: list[str], prefix: str", "str", "takes a list of words and a\n"
		"prefix, and returns the characters that come right after prefix in the\n"
		"words that start with it and are longer than it: each character once,\n"
		"in ASCII order, as a string"),
	"shortest_unique": ("words: list[str]", "list[str]", "takes a list of different words\n"
		"and returns, for each word in the order of the list, its shortest\n"
		"prefix that no other word of the list starts with; the whole word if\n"
		"every prefix of it starts another word too"),
}

EXERCISE = Exercise(
	name="word_complete",
	language="python",
	kind="function",
	assignment_name="complete_${rule}",
	expected_files=("complete_${rule}.py",),
	allowed_functions=(),
	themes=("prefix_complete",),
	params=(Param("rule", tuple(RULES), {rule: text for rule, (_, _, text) in RULES.items()}),),
	subject=(
		"Write a function that\n"
		"$rule.\n"
		"\n"
		"A word starts with a prefix when its first characters are the prefix: every\n"
		"word starts with the empty prefix, and with itself. The case matters.\n"
		"\n"
		"The function returns its result and prints nothing.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"$prototype"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=harness("complete_${rule}"),
	call=call,
	prototype=lambda name, params: f"def {name}({RULES[params['rule']][0]}) -> {RULES[params['rule']][1]}:",
	examples=lambda params: {
		"top_k": (case(["car", "cat", "car", "cart", "dog", "cat", "car"], "ca", 2),),
		"next_letters": (case(["car", "cat", "cart", "ca", "dog"], "ca"),),
		"shortest_unique": (case(["dog", "cat", "car", "cart"]),),
	}[params["rule"]],
)
