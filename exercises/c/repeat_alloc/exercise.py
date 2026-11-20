"""repeat_alloc: an original function model in the style of "repeat each letter".

The student writes a function that returns a new string, allocated with
malloc, where some characters are repeated: the vowels twice, the letters
by their case, or each character by its index. Each letter repeated by its
rank in the alphabet, the real 42 subject, is not one of the variants.
"""

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

def times(char, index, rule):
	if rule == "vowels_twice":
		return 2 if char in "aeiouAEIOU" else 1
	if rule == "by_case":
		return 3 if "A" <= char <= "Z" else 2 if "a" <= char <= "z" else 1
	return index % 3 + 1

def oracle(params, test):
	"""Return what the test main prints: the new string, then a newline."""
	return "".join(char * times(char, index, params["rule"]) for index, char in enumerate(test.args[0])) + "\n"

def generate_tests(params, rng):
	texts = ["", "Hello", "Ab1", "abcd", "AEIOU aeiou", "x", "42 is 42!", "MiXeD CaSe"]
	for _ in range(8):
		texts.append("".join(rng.choice("aEiBc 1Z") for _ in range(rng.randint(1, 14))))
	return [TestCase((text,)) for text in texts]

# The test main: av[1] is the string; it prints the new string, then frees it.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

char	*ft_repeat_${rule}(char *str);

int	main(int ac, char **av)
{
	char	*made;

	(void)ac;
	made = ft_repeat_${rule}(av[1]);
	printf("%s\\n", made ? made : "(null)");
	free(made);
	return (0);
}
"""

EXERCISE = Exercise(
	name="repeat_alloc",
	language="c",
	kind="function",
	assignment_name="ft_repeat_${rule}",
	expected_files=("ft_repeat_${rule}.c",),
	allowed_functions=("malloc",),
	themes=("letter_repeat",),
	params=(
		Param("rule", ("vowels_twice", "by_case", "by_index"), {
			"vowels_twice": "each vowel (a, e, i, o, u, in either case) twice, every other\n"
				"character once",
			"by_case": "each uppercase letter 3 times, each lowercase letter twice, every\n"
				"other character once",
			"by_index": "each character as many times as its index, counted from 0, modulo 3,\n"
				"plus 1: the first character once, the second twice, the third 3 times,\n"
				"the fourth once again, and so on",
		}),
	),
	subject=(
		"Write a function that returns a new string, allocated with malloc, made of\n"
		"the characters of str in order, each one repeated:\n"
		"$rule.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t*$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	check_leaks=True,
	examples=lambda params: {
		"vowels_twice": (TestCase(("Hello",)),),
		"by_case": (TestCase(("Ab1",)),),
		"by_index": (TestCase(("abcd",)),),
	}[params["rule"]],
)
