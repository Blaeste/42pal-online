"""split_fields: an original function model on the theme "split a string".

The student writes a function that cuts a string into fields, returned as
a NULL-terminated array of strings allocated with malloc. The variants
change the separator and whether empty fields are kept. Whitespace with
empty fields left out is the real exam subject of this theme: forbidden.
"""

import re

from pal42.model import Exercise, Param, TestCase
from pal42.subject import c_string

# The characters each separator value cuts at.
SEPARATORS = {"whitespace": " \t\n", "comma": ",", "colon": ":", "semicolon": ";"}

def fields(text, separators, keep):
	"""Cut `text` at each of `separators`; drop the empty fields unless `keep`."""
	parts = re.split("[" + re.escape(separators) + "]", text)
	return parts if keep else [part for part in parts if part]

def oracle(params, test):
	"""Return what the test main prints: each field between brackets, one a line."""
	parts = fields(test.args[0], SEPARATORS[params["separator"]], params["empty"] == "keep")
	return "".join(f"[{part}]\n" for part in parts)

# Letters and every separator of every variant, so that each variant meets
# its own separator next to the others.
ALPHABET = "ab ,:;\t"

def generate_tests(params, rng):
	"""Return the test cases of a variant: edge cases first, then random ones.

	The first six are the ones checked under valgrind (see MAX_LEAK_TESTS):
	empty string, one field, separators only, separators in a row... The
	same rng gives the same tests, for every variant.
	"""
	tests = [
		TestCase(("",)),
		TestCase(("one",)),
		TestCase((",:; \t",)),
		TestCase(("a,,b::c;;d  e",)),
		TestCase((",a:b;c d,",)),
		TestCase(("  a  b\tc\nd  ",)),
		TestCase(("x,y:z;w",)),
		TestCase(("no separator",)),
	]
	for _ in range(10):
		text = "".join(rng.choice(ALPHABET) for _ in range(rng.randint(0, 16)))
		tests.append(TestCase((text,)))
	return tests

# The test main: prints each field between brackets, then frees it, then the
# array, so that valgrind only finds what the student's function lost.
HARNESS = """#include <stdio.h>
#include <stdlib.h>

char	**ft_split_${separator}_${empty}(char *str);

int	main(int ac, char **av)
{
	char	**fields;
	int		i;

	(void)ac;
	fields = ft_split_${separator}_${empty}(av[1]);
	if (!fields)
	{
		printf("(null)\\n");
		return (0);
	}
	i = 0;
	while (fields[i])
	{
		printf("[%s]\\n", fields[i]);
		free(fields[i]);
		i++;
	}
	free(fields);
	return (0);
}
"""

EXERCISE = Exercise(
	name="split_fields",
	language="c",
	kind="function",
	assignment_name="ft_split_${separator}_${empty}",
	expected_files=("ft_split_${separator}_${empty}.c",),
	allowed_functions=("malloc", "free"),
	themes=("string_split",),
	params=(
		Param("separator", ("whitespace", "comma", "colon", "semicolon"), {
			"whitespace": "each space, tab or newline",
			"comma": "each comma (,)",
			"colon": "each colon (:)",
			"semicolon": "each semicolon (;)",
		}),
		Param("empty", ("skip", "keep"), {
			"skip": "Empty fields (two separators in a row, or one at an end) are left out",
			"keep": "Empty fields (two separators in a row, or one at an end) are kept, as \"\"",
		}),
	),
	# Each hole starts a line, so that the lines stay under 80 characters.
	subject=(
		"Write a function that cuts the string str into fields, at\n"
		"$separator.\n"
		"$empty.\n"
		"\n"
		"It returns an array of the fields, ended by a NULL pointer. The array and\n"
		"each field are allocated with malloc. With no field at all, the array only\n"
		"holds NULL.\n"
		"\n"
		"In the examples, each field is shown between brackets, one per line.\n"
		"\n"
		"Your function must be declared as follows:\n"
		"\n"
		"char\t**$assignment(char *str);"
	),
	oracle=oracle,
	generate_tests=generate_tests,
	harness=HARNESS,
	check_leaks=True,
	call=lambda name, test: f"{name}({c_string(test.args[0])})",
	examples=(
		TestCase(("a,,b",)),
		TestCase(("one:two;three four",)),
		TestCase(("",)),
	),
	# Whitespace, empty fields left out: that is the real exam subject.
	forbidden=({"separator": "whitespace", "empty": "skip"},),
)
