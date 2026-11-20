"""Tests of pal42.grader: grading a student's rendu, like the moulinette.

Run all the tests from the project root with: python3 -m unittest -v
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from pal42.catalog import load_catalog
from pal42.grader import MAX_LEAK_TESTS, grade
from pal42.model import TestCase
from pal42.runners.c import CRunner
from pal42.variant import Variant
from tests.helpers import ECHO, ECHO_OK, echo_oracle, echo_tests, make_exercise

class TestGrade(unittest.TestCase):
	"""grade(variant, rendu, runner) on a made-up exercise."""

	def setUp(self):
		"""rendu/ stands for ~/42pal_exam/rendu/<name>/ in each test."""
		self.tmp = tempfile.TemporaryDirectory()
		self.rendu = Path(self.tmp.name)

	def tearDown(self):
		self.tmp.cleanup()

	def hand_in(self, code, name="echo_first.c"):
		"""Write the student's file in the rendu folder."""
		(self.rendu / name).write_text(code, encoding="utf-8")

	def test_right_solution_passes(self):
		"""Every test gives the oracle's output: passed, no trace."""
		self.hand_in(ECHO_OK)
		result = grade(ECHO, self.rendu, CRunner())
		self.assertTrue(result.passed, result.trace)
		self.assertEqual(result.trace, "")
		self.assertEqual((result.tests_passed, result.tests_total), (3, 3))

	def test_progress_is_called_before_each_test(self):
		"""progress(number, total) lets the shell show "test 2/3" while grading."""
		self.hand_in(ECHO_OK)
		calls = []
		grade(ECHO, self.rendu, CRunner(), progress=lambda number, total: calls.append((number, total)))
		self.assertEqual(calls, [(1, 3), (2, 3), (3, 3)])

	def test_missing_newline_fails_with_a_diff_trace(self):
		"""No \\n at the end: stopped at test 1, student in -, moulinette in +."""
		self.hand_in(ECHO_OK.replace('\twrite(1, "\\n", 1);\n', ""))
		result = grade(ECHO, self.rendu, CRunner())
		self.assertFalse(result.passed)
		self.assertEqual(result.tests_passed, 0)
		self.assertEqual(result.trace, (
			"= Test 1 " + "=" * 71 + "\n"
			"$> ./echo_first hello | cat -e\n"
			"--- student\n"
			"+++ moulinette\n"
			"-hello\n"
			"+hello$\n"
			"\n"
			"Diff KO\n"
		))

	def test_crash_gives_its_own_message_instead_of_a_diff(self):
		"""A segfault: the command of the test, then "Segmentation fault"."""
		self.hand_in(ECHO_OK.replace("\tint\tn;\n", "\tint\tn;\n\n\t*(volatile int *)0 = 0;\n"))
		result = grade(ECHO, self.rendu, CRunner())
		self.assertFalse(result.passed)
		self.assertEqual(result.trace, (
			"= Test 1 " + "=" * 71 + "\n"
			"$> ./echo_first hello | cat -e\n"
			"\n"
			"Segmentation fault\n"
		))

	def test_endless_program_gives_a_timeout_message(self):
		"""A program that never ends: "Timeout" instead of a diff."""
		self.hand_in(ECHO_OK.replace("\tint\tn;\n", "\tint\tn;\n\n\twhile (1)\n\t\t;\n"))
		result = grade(ECHO, self.rendu, CRunner(timeout=0.5))
		self.assertFalse(result.passed)
		self.assertTrue(result.trace.endswith("\nTimeout\n"), result.trace)

	def test_compilation_error_gives_the_compiler_output(self):
		"""-Werror refuses an unused variable: the compiler's words, no test run."""
		self.hand_in(ECHO_OK.replace("\tint\tn;\n", "\tint\tn;\n\tint\tunused;\n"))
		result = grade(ECHO, self.rendu, CRunner())
		self.assertFalse(result.passed)
		self.assertEqual(result.tests_passed, 0)
		self.assertTrue(result.trace.startswith("= Compilation ="), result.trace)
		self.assertIn("$> cc -Wall -Wextra -Werror echo_first.c -o echo_first\n", result.trace)
		self.assertIn("unused variable", result.trace)
		self.assertTrue(result.trace.endswith("\nCompilation KO\n"), result.trace)

	def test_missing_file_is_named_in_the_trace(self):
		"""A wrong file name (echo.c): the expected one is named, nothing compiled."""
		self.hand_in(ECHO_OK, name="echo.c")
		result = grade(ECHO, self.rendu, CRunner())
		self.assertFalse(result.passed)
		self.assertEqual(result.trace, (
			"= Files " + "=" * 72 + "\n"
			"Missing file: echo_first.c\n"
			"\n"
			"Files KO\n"
		))

	def test_forbidden_function_fails_even_with_the_right_output(self):
		"""printf when only write is allowed: refused before any test is run."""
		self.hand_in(
			'#include <stdio.h>\n\nint\tmain(int ac, char **av)\n{\n'
			'\tif (ac == 2)\n\t\tprintf("%s", av[1]);\n\tprintf("%c", 10);\n\treturn (0);\n}\n'
		)
		result = grade(ECHO, self.rendu, CRunner())
		self.assertFalse(result.passed)
		self.assertEqual(result.trace, (
			"= Forbidden functions " + "=" * 58 + "\n"
			"Forbidden function: printf\n"
			"Allowed functions: write\n"
			"\n"
			"Functions KO\n"
		))

	def test_memset_put_by_the_compiler_is_not_refused(self):
		"""= {0} on an array: the compiler calls memset itself; the student did not."""
		self.hand_in(ECHO_OK.replace("\tint\tn;\n",
			"\tint\tn;\n\tchar\tbuffer[512] = {0};\n\n\t(void)buffer;\n", 1))
		result = grade(ECHO, self.rendu, CRunner())
		self.assertTrue(result.passed, result.trace)

	def test_memset_written_by_the_student_is_refused(self):
		"""memset in the code: refused, like any function that is not allowed."""
		self.hand_in("#include <string.h>\n" + ECHO_OK.replace("\tint\tn;\n",
			"\tint\tn;\n\tchar\tbuffer[512];\n\n\tmemset(buffer, 0, 512);\n", 1))
		result = grade(ECHO, self.rendu, CRunner())
		self.assertIn("Forbidden function: memset", result.trace)

	def test_memset_named_in_a_comment_or_a_string_is_not_a_call(self):
		self.hand_in(ECHO_OK.replace("\tint\tn;\n",
			"\tint\tn;\n\tchar\tbuffer[512] = {0}; /* not memset */\n\n"
			"\t(void)buffer;\n\t(void)\"memset\";\n", 1))
		result = grade(ECHO, self.rendu, CRunner())
		self.assertTrue(result.passed, result.trace)

SHIFT_FORWARD_2 = r"""#include <unistd.h>

int	main(int ac, char **av)
{
	char	c;
	int		i;

	if (ac == 2)
	{
		i = 0;
		while (av[1][i])
		{
			c = av[1][i];
			if (c >= 'a' && c <= 'z')
				c = (c - 'a' + 2) % 26 + 'a';
			else if (c >= 'A' && c <= 'Z')
				c = (c - 'A' + 2) % 26 + 'A';
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
"""

class TestRealExercise(unittest.TestCase):
	"""A real C solution, graded on all the tests of a real exercise."""

	def test_c_solution_of_shift_letters_passes_every_test(self):
		"""forward_shift_2 (every letter): our C solution agrees with the oracle."""
		exo = load_catalog().exercises["shift_letters"]
		variant = Variant(exo, 0, {"shift": "2", "direction": "forward", "letters": "all"})
		with tempfile.TemporaryDirectory() as rendu:
			(Path(rendu) / "forward_shift_2.c").write_text(SHIFT_FORWARD_2, encoding="utf-8")
			result = grade(variant, rendu, CRunner())
		self.assertTrue(result.passed, result.trace)
		self.assertEqual(result.tests_passed, result.tests_total)

COUNT_HARNESS = r"""#include <stdio.h>

int	ft_count(char *str, char c);

int	main(int ac, char **av)
{
	(void)ac;
	printf("%d\n", ft_count(av[1], av[2][0]));
	return (0);
}
"""

# A made-up function exercise: count the c in str. Nothing is allowed.
COUNT = Variant(
	make_exercise(
		name="count", kind="function", assignment_name="ft_count",
		expected_files=("ft_count.c",), allowed_functions=(), harness=COUNT_HARNESS,
		oracle=lambda params, test: f"{test.args[0].count(test.args[1])}\n",
		call=lambda name, test: f'{name}("{test.args[0]}", \'{test.args[1]}\')',
		generate_tests=lambda params, rng: [
			TestCase(("hello", "l")), TestCase(("", "x")), TestCase(("aaa", "a")),
		],
	),
	0, {"mode": "common"},
)

COUNT_OK = r"""int	ft_count(char *str, char c)
{
	int	n;

	n = 0;
	while (*str)
		if (*str++ == c)
			n++;
	return (n);
}
"""

class TestGradeFunction(unittest.TestCase):
	"""grade() on a function exercise: the test main calls the student's function."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.rendu = Path(self.tmp.name)

	def tearDown(self):
		self.tmp.cleanup()

	def grade(self, code):
		(self.rendu / "ft_count.c").write_text(code, encoding="utf-8")
		return grade(COUNT, self.rendu, CRunner())

	def test_right_function_passes_though_the_test_main_uses_printf(self):
		"""printf is in the test main, not in the rendu: nothing is refused."""
		result = self.grade(COUNT_OK)
		self.assertTrue(result.passed, result.trace)
		self.assertEqual(result.tests_passed, 3)

	def test_function_off_by_one_fails(self):
		"""Counting from 1 instead of 0: Diff KO at the first test."""
		result = self.grade(COUNT_OK.replace("n = 0;", "n = 1;"))
		self.assertFalse(result.passed)
		self.assertIn("-3$\n+2$", result.trace)
		# A function's trace shows the call, not a command line.
		self.assertIn("$> ft_count(\"hello\", 'l')\n", result.trace)

	def test_rendu_with_a_main_gives_a_clear_error(self):
		"""A main in the rendu: say so, instead of a cryptic link error."""
		result = self.grade(COUNT_OK + "\nint\tmain(void)\n{\n\treturn (0);\n}\n")
		self.assertFalse(result.passed)
		self.assertIn("contain a main", result.trace)
		self.assertTrue(result.trace.endswith("\nFiles KO\n"), result.trace)

	def test_forbidden_function_in_the_student_code_is_refused(self):
		"""strlen in the student's function is refused, even with the test main."""
		result = self.grade(
			"#include <string.h>\n\nint\tft_count(char *str, char c)\n{\n"
			"\t(void)c;\n\treturn (strlen(str));\n}\n"
		)
		self.assertIn("Forbidden function: strlen", result.trace)
		self.assertNotIn("printf", result.trace)

LEAKY_ECHO = r"""#include <stdlib.h>
#include <unistd.h>

int	main(int ac, char **av)
{
	char	*copy;
	int		n;

	copy = malloc(64);
	if (ac == 2)
	{
		n = 0;
		while (av[1][n])
			n++;
		write(1, av[1], n);
	}
	write(1, "\n", 1);
	(void)copy;
	return (0);
}
"""
CLEAN_ECHO = LEAKY_ECHO.replace("\t(void)copy;", "\tfree(copy);")

def echo_with(check_leaks):
	"""echo_first where malloc and free are allowed, leaks checked or not."""
	exo = make_exercise(
		name="echo_first", expected_files=("echo_first.c",),
		allowed_functions=("write", "malloc", "free"), check_leaks=check_leaks,
		oracle=echo_oracle, generate_tests=echo_tests,
	)
	return Variant(exo, 0, {"mode": "common"})

class TestLeaks(unittest.TestCase):
	"""The leak check, for the exercises that ask for it."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.rendu = Path(self.tmp.name)

	def tearDown(self):
		self.tmp.cleanup()

	def grade(self, code, check_leaks=True, **options):
		(self.rendu / "echo_first.c").write_text(code, encoding="utf-8")
		return grade(echo_with(check_leaks), self.rendu, CRunner(), **options)

	@unittest.skipUnless(shutil.which("valgrind"), "valgrind is not installed")
	def test_leak_fails_with_valgrind_report(self):
		"""Right output but a malloc without free: Leaks KO, with the report."""
		result = self.grade(LEAKY_ECHO)
		self.assertFalse(result.passed)
		self.assertTrue(result.trace.startswith("= Test 1 ="), result.trace)
		self.assertIn("definitely lost", result.trace)
		self.assertTrue(result.trace.endswith("\nLeaks KO\n"), result.trace)

	@unittest.skipUnless(shutil.which("valgrind"), "valgrind is not installed")
	def test_clean_solution_passes(self):
		"""Every malloc freed: passed, without warning."""
		result = self.grade(CLEAN_ECHO)
		self.assertTrue(result.passed, result.trace)
		self.assertEqual(result.warnings, ())

	@unittest.skipUnless(shutil.which("valgrind"), "valgrind is not installed")
	def test_leaks_are_checked_on_the_first_tests_only(self):
		"""valgrind is slow: it runs on MAX_LEAK_TESTS tests at most."""
		exo = make_exercise(
			name="echo_first", expected_files=("echo_first.c",),
			allowed_functions=("write", "malloc", "free"), check_leaks=True,
			oracle=echo_oracle,
			generate_tests=lambda params, rng: [TestCase(("word",))] * (MAX_LEAK_TESTS + 4),
		)
		(self.rendu / "echo_first.c").write_text(CLEAN_ECHO, encoding="utf-8")
		steps = []
		grade(Variant(exo, 0, {"mode": "common"}), self.rendu, CRunner(),
			progress=lambda number, total, step="output": steps.append(step))
		self.assertEqual(steps.count("memory"), MAX_LEAK_TESTS)

	def test_leaks_are_not_checked_unless_the_exercise_asks(self):
		"""check_leaks off: the leak is not looked for."""
		self.assertTrue(self.grade(LEAKY_ECHO, check_leaks=False).passed)

	def test_without_valgrind_it_passes_with_a_warning(self):
		"""valgrind missing: nothing crashes, a warning says it was not checked."""
		result = self.grade(LEAKY_ECHO, valgrind="no_such_valgrind")
		self.assertTrue(result.passed, result.trace)
		self.assertIn("valgrind", result.warnings[0])

LIST_HEADER = "#ifndef FT_LIST_H\n# define FT_LIST_H\n\ntypedef struct s_list\n{\n\tstruct s_list\t*next;\n\tint\t\t\t\tvalue;\n}\tt_list;\n\nint\tft_list_size(t_list *begin);\n\n#endif\n"

LIST_SIZE = '#include "ft_list.h"\n\nint\tft_list_size(t_list *begin)\n{\n\tint\tn;\n\n\tn = 0;\n\twhile (begin)\n\t{\n\t\tn++;\n\t\tbegin = begin->next;\n\t}\n\treturn (n);\n}\n'

# The test main builds a list of av[1] nodes with the student's header.
LIST_HARNESS = '#include <stdio.h>\n#include <stdlib.h>\n#include "ft_list.h"\n\nint\tmain(int ac, char **av)\n{\n\tt_list\tnodes[10];\n\tint\t\tn;\n\tint\t\ti;\n\n\t(void)ac;\n\tn = atoi(av[1]);\n\ti = 0;\n\twhile (i < n)\n\t{\n\t\tnodes[i].next = (i + 1 < n) ? &nodes[i + 1] : NULL;\n\t\ti++;\n\t}\n\tprintf("%d\\n", ft_list_size(n ? nodes : NULL));\n\treturn (0);\n}\n'

def list_size_variant(**changes):
	"""A made-up function exercise whose rendu has a header and a .c."""
	fields = dict(
		name="list_size", kind="function", assignment_name="ft_list_size",
		expected_files=("ft_list.h", "ft_list_size.c"), allowed_functions=(),
		harness=LIST_HARNESS, oracle=lambda params, test: f"{test.args[0]}\n",
		generate_tests=lambda params, rng: [TestCase(("0",)), TestCase(("1",)), TestCase(("5",))],
	)
	fields.update(changes)
	return Variant(make_exercise(**fields), 0, {"mode": "common"})

class TestSeveralFiles(unittest.TestCase):
	"""Rendus with a header, handed in by the student or given by the exercise."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.rendu = Path(self.tmp.name)

	def tearDown(self):
		self.tmp.cleanup()

	def hand_in(self, files):
		for name, code in files.items():
			(self.rendu / name).write_text(code, encoding="utf-8")

	def test_a_header_and_a_c_file_handed_in_pass(self):
		"""ft_list.h and ft_list_size.c: the test main uses the student's header."""
		self.hand_in({"ft_list.h": LIST_HEADER, "ft_list_size.c": LIST_SIZE})
		result = grade(list_size_variant(), self.rendu, CRunner())
		self.assertTrue(result.passed, result.trace)

	def test_a_missing_header_is_named(self):
		"""Only the .c handed in: the header is missing, and named."""
		self.hand_in({"ft_list_size.c": LIST_SIZE})
		result = grade(list_size_variant(), self.rendu, CRunner())
		self.assertIn("Missing file: ft_list.h", result.trace)

	def test_a_header_given_by_the_exercise_needs_not_be_handed_in(self):
		"""ft_list.h is given: the student hands in ft_list_size.c only."""
		self.hand_in({"ft_list_size.c": LIST_SIZE})
		variant = list_size_variant(expected_files=("ft_list_size.c",),
			provided_files={"ft_list.h": LIST_HEADER})
		result = grade(variant, self.rendu, CRunner())
		self.assertTrue(result.passed, result.trace)
