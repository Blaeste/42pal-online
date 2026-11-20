"""Tests of the char_position exercise (a function): its oracle and variants.

The expected outputs below are worked out by hand, never by the oracle:
that is what checks the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import tempfile
import unittest
from pathlib import Path
from random import Random
from runpy import run_path

from pal42.grader import grade
from pal42.model import TestCase
from pal42.runners.c import CRunner
from pal42.subject import render
from pal42.variant import Variant

# run_path runs exercise.py and returns its global names, EXERCISE among them.
EXERCISE_FILE = Path(__file__).resolve().parent.parent / "exercises/c/char_position/exercise.py"
EXERCISE = run_path(str(EXERCISE_FILE))["EXERCISE"]

def output(text, char, mode, case="exact"):
	"""What the test main prints: the function's result for (text, char)."""
	return EXERCISE.oracle({"mode": mode, "case": case}, TestCase((text, char)))

class TestOracle(unittest.TestCase):
	"""What ft_char_<mode> must return, worked out by hand."""

	def test_count(self):
		"""count: how many times c is in str; case matters only if exact."""
		self.assertEqual(output("hello world", "o", "count"), "2\n")
		self.assertEqual(output("", "a", "count"), "0\n")
		# Exact: h is not H. Any case: H counts as h, and A as a.
		self.assertEqual(output("Hello", "h", "count"), "0\n")
		self.assertEqual(output("Hello", "h", "count", case="any"), "1\n")
		self.assertEqual(output("AaBbAa", "a", "count", case="any"), "4\n")

	def test_first_and_last_index(self):
		"""first/last: the index of the first/last c, -1 when there is none."""
		# h e l l o: the l are at 2 and 3.
		self.assertEqual(output("hello", "l", "first"), "2\n")
		self.assertEqual(output("hello", "l", "last"), "3\n")
		self.assertEqual(output("hello", "z", "first"), "-1\n")
		self.assertEqual(output("", "x", "last"), "-1\n")
		# Exact: no h in Hello. Any case: H at 0; the last a of abcABC is A at 3.
		self.assertEqual(output("Hello", "h", "first"), "-1\n")
		self.assertEqual(output("Hello", "h", "first", case="any"), "0\n")
		self.assertEqual(output("abcABC", "a", "last", case="any"), "3\n")

LAST_ANY = r"""int	ft_char_last(char *str, char c)
{
	int		i;
	int		last;
	char	letter;

	if (c >= 'A' && c <= 'Z')
		c = c - 'A' + 'a';
	last = -1;
	i = 0;
	while (str[i])
	{
		letter = str[i];
		if (letter >= 'A' && letter <= 'Z')
			letter = letter - 'A' + 'a';
		if (letter == c)
			last = i;
		i++;
	}
	return (last);
}
"""

class TestVariants(unittest.TestCase):
	"""The variants of char_position, and a real C solution graded."""

	def test_generated_tests_are_reproducible_with_one_character_each(self):
		"""Same seed, same tests; c is always one character (av[2][0])."""
		params = EXERCISE.combinations()[0]
		tests = EXERCISE.generate_tests(params, Random(7))
		self.assertEqual(tests, EXERCISE.generate_tests(params, Random(7)))
		self.assertGreaterEqual(len(tests), 10)
		self.assertTrue(all(len(test.args) == 2 and len(test.args[1]) == 1 for test in tests))
		self.assertIn(TestCase(("", "a")), tests)

	def test_every_variant_has_a_subject_with_its_prototype(self):
		"""3 modes x 2 cases: 6 subjects, lines of 80 at most, the prototype in."""
		self.assertEqual(len(EXERCISE.combinations()), 6)
		for params in EXERCISE.combinations():
			variant = Variant(EXERCISE, 0, params)
			subject = render(variant)
			self.assertIn(f"int\t{variant.name}(char *str, char c);", subject)
			for line in subject.splitlines():
				self.assertLessEqual(len(line), 80, f"{params} : {line}")

	def test_a_c_solution_passes_with_the_test_main(self):
		"""ft_char_last (any case), compiled with the test main: every test OK."""
		variant = Variant(EXERCISE, 0, {"mode": "last", "case": "any"})
		with tempfile.TemporaryDirectory() as rendu:
			(Path(rendu) / "ft_char_last.c").write_text(LAST_ANY, encoding="utf-8")
			result = grade(variant, rendu, CRunner())
		self.assertTrue(result.passed, result.trace)
		self.assertEqual(result.tests_passed, result.tests_total)

	def test_the_subject_has_examples_written_as_calls(self):
		"""ft_char_count("hello world", 'o') gives 2, written by the oracle."""
		subject = render(Variant(EXERCISE, 0, {"mode": "count", "case": "exact"}))
		self.assertIn("Examples:\n\nft_char_count(\"hello world\", 'o')\n2$\n", subject)
