"""Tests of pal42.runners.c: compiling a student's C files.

Run all the tests from the project root with: python3 -m unittest -v
"""

import os
import signal
import tempfile
import time
import unittest
from pathlib import Path

from pal42.model import TestCase
from pal42.runners.c import CRunner

HELLO = '#include <unistd.h>\n\nint\tmain(void)\n{\n\twrite(1, "hello\\n", 6);\n\treturn (0);\n}\n'
UNUSED = "int\tmain(void)\n{\n\tint\tx;\n\n\treturn (0);\n}\n"

class TestCompile(unittest.TestCase):
	"""CRunner.compile(sources, workdir, name) builds the student's program."""

	def setUp(self):
		"""Each test gets a folder for the student's files and a work folder."""
		self.tmp = tempfile.TemporaryDirectory()
		self.rendu = Path(self.tmp.name) / "rendu"
		self.work = Path(self.tmp.name) / "work"
		self.rendu.mkdir()
		self.work.mkdir()

	def tearDown(self):
		self.tmp.cleanup()

	def write(self, name, code):
		"""Write a student's file in the rendu folder and return its path."""
		path = self.rendu / name
		path.write_text(code, encoding="utf-8")
		return path

	def test_valid_file_compiles(self):
		"""A correct .c gives an executable program in the work folder."""
		result = CRunner().compile([self.write("hello.c", HELLO)], self.work, "hello")
		self.assertTrue(result.ok, result.output)
		self.assertTrue(os.access(result.binary, os.X_OK))
		self.assertEqual(result.binary.parent, self.work)

	def test_unused_variable_fails_and_the_error_is_captured(self):
		"""-Werror turns the warning into an error; its message is kept."""
		result = CRunner().compile([self.write("bad.c", UNUSED)], self.work, "bad")
		self.assertFalse(result.ok)
		self.assertIsNone(result.binary)
		self.assertIn("unused variable", result.output)

	def test_error_names_the_file_without_its_folder(self):
		"""The files are compiled in the work folder: bad.c:3:6, not a long path."""
		result = CRunner().compile([self.write("bad.c", UNUSED)], self.work, "bad")
		self.assertTrue(result.output.startswith("bad.c:"), result.output)
		self.assertNotIn(self.tmp.name, result.output)
		# The student's folder stays as it was: no program, no copy.
		self.assertEqual([path.name for path in self.rendu.iterdir()], ["bad.c"])

	def test_compile_keeps_an_object_per_student_file(self):
		"""Each student file gives an object (.o) in the work folder, for nm."""
		result = CRunner().compile([self.write("hello.c", HELLO)], self.work, "hello")
		self.assertEqual(result.objects, (self.work / "hello.o",))
		self.assertTrue(result.objects[0].exists())

	def test_extra_sources_are_linked_with_the_student_files(self):
		"""A test main given as extra calls the student's function."""
		function = self.write("add.c", "int\tadd(int a, int b)\n{\n\treturn (a + b);\n}\n")
		main = self.work / "test_main.c"
		main.write_text(
			'#include <stdio.h>\n\nint\tadd(int a, int b);\n\n'
			'int\tmain(void)\n{\n\tprintf("%d\\n", add(2, 3));\n\treturn (0);\n}\n',
			encoding="utf-8",
		)
		result = CRunner().compile([function], self.work, "add", extra=[main])
		self.assertTrue(result.ok, result.output)
		self.assertEqual(CRunner().run(result.binary, TestCase()).stdout, b"5\n")
		self.assertEqual(result.objects, (self.work / "add.o",))

	def test_a_header_among_the_sources_is_used_not_compiled(self):
		"""ft_list.h + ft_list.c: only the .c gives an object; the header is included."""
		header = self.write("ft_list.h", "#ifndef FT_LIST_H\n# define FT_LIST_H\nint\tsize(void);\n#endif\n")
		code = self.write("ft_list.c", '#include "ft_list.h"\n\nint\tsize(void)\n{\n\treturn (42);\n}\n')
		main = self.work / "test_main.c"
		main.write_text('#include <stdio.h>\n#include "ft_list.h"\n\nint\tmain(void)\n'
			'{\n\tprintf("%d\\n", size());\n\treturn (0);\n}\n', encoding="utf-8")
		result = CRunner().compile([header, code], self.work, "prog", extra=[main])
		self.assertTrue(result.ok, result.output)
		self.assertEqual(result.objects, (self.work / "ft_list.o",))
		self.assertEqual(CRunner().run(result.binary, TestCase()).stdout, b"42\n")

	def test_compile_command_can_be_changed(self):
		"""An exam can give its own command: without -Werror, a warning passes."""
		runner = CRunner(("cc", "-Wall"))
		result = runner.compile([self.write("bad.c", UNUSED)], self.work, "bad")
		self.assertTrue(result.ok, result.output)
		self.assertIn("warning: unused variable", result.output)

	def test_missing_compiler_gives_a_clear_error(self):
		"""A compiler that is not installed: a failed compilation, not a crash."""
		runner = CRunner(("no_such_cc_42pal", "-Wall"))
		result = runner.compile([self.write("hello.c", HELLO)], self.work, "hello")
		self.assertFalse(result.ok)
		self.assertIn("not found", result.output)
		self.assertIn("no_such_cc_42pal", result.output)

	def test_source_already_in_the_work_folder_compiles(self):
		"""No copy is needed when the file is already in the work folder."""
		source = self.work / "hello.c"
		source.write_text(HELLO, encoding="utf-8")
		result = CRunner().compile([source], self.work, "hello")
		self.assertTrue(result.ok, result.output)

# Small programs for the run tests. raw strings: the \n stay for C to read.
PRINT_ARGS = r"""#include <unistd.h>

int	main(int ac, char **av)
{
	for (int i = 1; i < ac; i++)
	{
		int	n = 0;
		while (av[i][n])
			n++;
		write(1, av[i], n);
		write(1, "\n", 1);
	}
	return (ac - 1);
}
"""

COPY_STDIN = r"""#include <unistd.h>

int	main(void)
{
	char	buffer[64];
	ssize_t	n;

	while ((n = read(0, buffer, 64)) > 0)
		write(1, buffer, n);
	return (0);
}
"""

ENDLESS_LOOP = "int\tmain(void)\n{\n\twhile (1)\n\t\t;\n}\n"

# volatile: without it, clang deletes the write to 0 and -Werror refuses it.
SEGFAULT = "int\tmain(void)\n{\n\t*(volatile int *)0 = 0;\n\treturn (0);\n}\n"

# Starts a child that loops forever, prints its pid, then loops too.
FORK_LOOP = r"""#include <stdio.h>
#include <unistd.h>

int	main(void)
{
	pid_t	pid;

	pid = fork();
	if (pid == 0)
		while (1)
			;
	printf("%d\n", pid);
	fflush(stdout);
	while (1)
		;
}
"""

# Starts a child that loops forever, prints its pid, then ends at once.
FORK_AND_EXIT = r"""#include <stdio.h>
#include <unistd.h>

int	main(void)
{
	pid_t	pid;

	pid = fork();
	if (pid == 0)
		while (1)
			;
	printf("%d\n", pid);
	return (0);
}
"""

ENDLESS_OUTPUT = r"""#include <unistd.h>

int	main(void)
{
	while (1)
		write(1, "spam spam spam\n", 15);
}
"""

class TestRun(unittest.TestCase):
	"""CRunner.run(program, test) runs the student's program on one test."""

	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.work = Path(self.tmp.name)

	def tearDown(self):
		self.tmp.cleanup()

	def build(self, code):
		"""Compile `code` and return the program."""
		source = self.work / "prog.c"
		source.write_text(code, encoding="utf-8")
		result = CRunner().compile([source], self.work, "prog")
		self.assertTrue(result.ok, result.output)
		return result.binary

	def test_run_gives_the_output_and_the_exit_code(self):
		"""The arguments reach the program; its output and exit code come back."""
		result = CRunner().run(self.build(PRINT_ARGS), TestCase(("hello", "a b")))
		self.assertEqual(result.stdout, b"hello\na b\n")
		self.assertEqual(result.exit_code, 2)
		self.assertIsNone(result.signal)
		self.assertFalse(result.timed_out)

	def test_standard_input_reaches_the_program(self):
		"""test.stdin is what the program reads on its standard input."""
		result = CRunner().run(self.build(COPY_STDIN), TestCase((), "line 1\nline 2\n"))
		self.assertEqual(result.stdout, b"line 1\nline 2\n")

	def test_endless_loop_is_stopped_by_the_timeout(self):
		"""A program that never ends is stopped: timed_out, no exit code."""
		result = CRunner(timeout=0.5).run(self.build(ENDLESS_LOOP), TestCase())
		self.assertTrue(result.timed_out)
		self.assertIsNone(result.exit_code)

	def test_segfault_is_recognized(self):
		"""A program killed by a signal: no exit code, the signal's name instead."""
		result = CRunner().run(self.build(SEGFAULT), TestCase())
		self.assertEqual(result.signal, "SIGSEGV")
		self.assertIsNone(result.exit_code)
		self.assertFalse(result.timed_out)

	def test_children_are_stopped_with_the_program(self):
		"""A child started with fork() is stopped too: no loop left running."""
		result = CRunner(timeout=0.5).run(self.build(FORK_LOOP), TestCase())
		child = int(result.stdout)
		# If the test fails, the child must still not be left running.
		self.addCleanup(stop_if_alive, child)
		self.assertTrue(result.timed_out)
		self.assertTrue(gone_within(child, seconds=2), f"the child {child} is still running")

	def test_child_left_behind_by_a_finished_program_is_stopped(self):
		"""The program ends normally but its child loops: the child is stopped."""
		result = CRunner(timeout=2).run(self.build(FORK_AND_EXIT), TestCase())
		child = int(result.stdout)
		self.addCleanup(stop_if_alive, child)
		self.assertEqual(result.exit_code, 0)
		self.assertFalse(result.timed_out)
		self.assertTrue(gone_within(child, seconds=2), f"the child {child} is still running")

	def test_endless_output_is_cut(self):
		"""Printing forever fills no memory: stopped past the size limit."""
		result = CRunner().run(self.build(ENDLESS_OUTPUT), TestCase(), max_output=10_000)
		self.assertEqual(result.signal, "SIGXFSZ")
		self.assertEqual(len(result.stdout), 10_000)

def stop_if_alive(pid):
	"""Kill `pid` if it still exists (cleanup after a failed test)."""
	try:
		os.kill(pid, signal.SIGKILL)
	except ProcessLookupError:
		pass

def gone_within(pid, seconds):
	"""True when the process `pid` disappears within `seconds`."""
	deadline = time.monotonic() + seconds
	while time.monotonic() < deadline:
		try:
			# Signal 0 sends nothing: it only checks that the process exists.
			os.kill(pid, 0)
		except ProcessLookupError:
			return True
		time.sleep(0.05)
	return False
