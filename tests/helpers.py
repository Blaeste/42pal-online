"""Helpers shared by the tests: a valid exercise to start from, and fakes.

Why: an Exercise needs 10 fields, but each test is about only one of them.
make_exercise() builds a valid exercise with default values, and a test
replaces only the fields it is about:

	from tests.helpers import make_exercise

	exo = make_exercise()                    # the default char_filter exercise
	exo = make_exercise(kind="fonction")     # same, but kind is "fonction"
	exo = make_exercise(                     # several fields replaced at once
		subject="Display $mode.",
		forbidden=({"mode": "common"},),
	)

Not a test module itself (its name does not start with test_), so unittest
does not look for tests in it.
"""

import os

from pal42.model import Exercise, Param, TestCase
from pal42.variant import Variant

# An Exercise must be given two functions (like function pointers in C):
# the oracle, which computes the expected output, and the test generator.
# The tests of the model and of the draw never grade anything, so these
# do nothing; they only fill the two fields.

def fake_oracle(params, test):
	"""Stand-in oracle, for tests that never grade."""
	return ""

def fake_generate_tests(params, rng):
	"""Stand-in test generator, for tests that never ask for test cases."""
	return []

def make_exercise(**changes):
	"""Build a valid exercise, with the fields given in `changes` replaced.

	Each test changes only the field it is about, so the rest stays valid.
	Any field of Exercise can be replaced, by its name (see pal42/model.py).
	"""
	# **changes gathers the named arguments into a dict:
	# make_exercise(kind="fonction") gives changes = {"kind": "fonction"}.

	# The default values: together, they make a valid exercise.
	fields = dict(
		name="char_filter",
		language="c",
		kind="program",
		expected_files=("char_filter.c",),
		allowed_functions=("write",),
		themes=("char_sets",),
		params=(Param("mode", ("common", "only_first")),),
		subject="Display the characters $mode, without doubles.",
		oracle=fake_oracle,
		generate_tests=fake_generate_tests,
	)
	# update replaces the default values by the ones given in changes;
	# the fields that are not in changes keep their default value.
	fields.update(changes)
	# **fields unpacks the dict back into named arguments: the same as
	# Exercise(name="char_filter", language="c", kind="fonction", ...).
	return Exercise(**fields)

# A made-up exercise with a real oracle and tests, to grade C solutions:
# print the only argument, or just a newline.

def echo_oracle(params, test):
	"""Made-up exercise: print the only argument, or just a newline."""
	return test.args[0] + "\n" if len(test.args) == 1 else "\n"

def echo_tests(params, rng):
	"""The tests of the made-up exercise."""
	return [TestCase(("hello",)), TestCase(("a b",)), TestCase(())]

ECHO = Variant(
	make_exercise(name="echo_first", expected_files=("echo_first.c",),
		oracle=echo_oracle, generate_tests=echo_tests),
	0, {"mode": "common"},
)

ECHO_OK = r"""#include <unistd.h>

int	main(int ac, char **av)
{
	int	n;

	if (ac == 2)
	{
		n = 0;
		while (av[1][n])
			n++;
		write(1, av[1], n);
	}
	write(1, "\n", 1);
	return (0);
}
"""

def selected_exercises(names):
	"""The exercises the slow tests go through: all of them, or those of PAL42_EXERCISES.

	On GitHub, PAL42_EXERCISES holds the exercises that changed (see
	tools/ci_scope.py): "all", "none", or names separated by spaces. Unset,
	as on a machine of a contributor: all of them.
	"""
	wanted = os.environ.get("PAL42_EXERCISES", "all").split()
	if wanted == ["all"]:
		return list(names)
	return [name for name in names if name in wanted]
