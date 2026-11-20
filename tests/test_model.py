"""Tests of pal42.model: the data that describes an exercise and its checks.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest

from pal42.model import ExerciseError, Param, TestCase
from tests.helpers import make_exercise

class TestParam(unittest.TestCase):
	"""Building a Param."""

	def test_param_without_values_raises(self):
		"""A param with no value could never be drawn; its name is in the message."""
		with self.assertRaisesRegex(ExerciseError, "mode"):
			Param("mode", ())

	def test_text_of_a_value(self):
		"""The subject shows the text of a value, or the value itself if none."""
		texts = {"common": "that appear in both strings", "only_first": "of the first"}
		self.assertEqual(
			Param("mode", ("common", "only_first"), texts).text("common"),
			"that appear in both strings",
		)
		self.assertEqual(Param("mode", ("common", "only_first")).text("common"), "common")

	def test_texts_must_match_the_values(self):
		"""A text for an unknown value, or a value without text, is an error."""
		values = ("common", "only_first")
		with self.assertRaisesRegex(ExerciseError, "comon"):
			Param("mode", values, {"comon": "both", "only_first": "first"})
		with self.assertRaisesRegex(ExerciseError, "only_first"):
			Param("mode", values, {"common": "both"})

class TestExercise(unittest.TestCase):
	"""Building an Exercise and checking it as soon as it is created."""

	def test_valid_exercise_is_created(self):
		"""An exercise whose subject only uses its own params is accepted."""
		exo = make_exercise()
		self.assertEqual(exo.name, "char_filter")
		self.assertEqual(exo.params[0].values, ("common", "only_first"))

	def test_subject_with_unknown_param_raises(self):
		"""A `$hole` that matches no param is an error, named in the message."""
		with self.assertRaisesRegex(ExerciseError, "order"):
			make_exercise(subject="Display the characters $mode, in $order.")

	def test_assignment_name_with_unknown_param_raises(self):
		"""assignment_name is checked like the subject: its holes must be params."""
		with self.assertRaisesRegex(ExerciseError, "name.*order"):
			make_exercise(assignment_name="${order}_chars")

	def test_expected_files_with_unknown_param_raises(self):
		"""expected_files are checked like the subject: their holes must be params."""
		with self.assertRaisesRegex(ExerciseError, "expected file.*order"):
			make_exercise(expected_files=("${order}_chars.c",))

	def test_lone_dollar_in_subject_raises(self):
		"""A `$` that starts no hole is an error that gives its line; `$$` is the fix."""
		with self.assertRaisesRegex(ExerciseError, r"line 2.*\$\$"):
			make_exercise(subject="Display the characters $mode.\nEach costs 5$.")

	def test_forbidden_combination_with_unknown_param_raises(self):
		"""A forbidden combination that names no param would never match."""
		with self.assertRaisesRegex(ExerciseError, "order"):
			make_exercise(forbidden=({"mode": "common", "order": "first"},))

	def test_forbidden_combination_with_unknown_value_raises(self):
		"""A typo in a forbidden value would let the real subject be drawn."""
		with self.assertRaisesRegex(ExerciseError, "comon"):
			make_exercise(forbidden=({"mode": "comon"},))

	def test_every_combination_forbidden_raises(self):
		"""An exercise must leave at least one combination to draw."""
		with self.assertRaisesRegex(ExerciseError, "no combination"):
			make_exercise(forbidden=({"mode": "common"}, {"mode": "only_first"}))

	def test_unknown_kind_raises(self):
		"""kind must be "program" or "function", the two kinds the graders know."""
		with self.assertRaisesRegex(ExerciseError, "fonction"):
			make_exercise(kind="fonction")

	def test_function_exercise_needs_a_test_main(self):
		"""kind "function" needs a harness: the main that calls the function."""
		with self.assertRaisesRegex(ExerciseError, "test main"):
			make_exercise(kind="function")

	def test_program_exercise_has_no_test_main(self):
		"""A program has its own main: a harness would make two of them."""
		with self.assertRaisesRegex(ExerciseError, "test main"):
			make_exercise(harness="int\tmain(void)\n{\n\treturn (0);\n}\n")

	def test_function_examples_need_a_call(self):
		"""Examples of a function show calls: without call, an error says so."""
		with self.assertRaisesRegex(ExerciseError, "call"):
			make_exercise(kind="function", harness="int\tmain(void);\n", examples=(TestCase(),))
		make_exercise(kind="function", harness="int\tmain(void);\n", examples=(TestCase(),),
			call=lambda name, test: f"{name}()")

	def test_test_main_with_unknown_param_raises(self):
		"""The holes of the harness are checked like those of the subject."""
		with self.assertRaisesRegex(ExerciseError, "test main.*order"):
			make_exercise(kind="function", harness="int\tft_${order}(void);\n")

	def test_subject_may_name_the_assignment(self):
		"""$assignment is the name the student sees, for a prototype for example."""
		make_exercise(subject="int\t$assignment(char *str);")

	def test_a_given_file_is_not_an_expected_one_and_its_holes_are_checked(self):
		"""Given by the exercise or handed in by the student, not both."""
		with self.assertRaisesRegex(ExerciseError, "char_filter.c.*given"):
			make_exercise(provided_files={"char_filter.c": "int\tx;\n"})
		with self.assertRaisesRegex(ExerciseError, "given file.*order"):
			make_exercise(provided_files={"point.h": "/* ${order} */\n"})

	def test_unknown_language_raises(self):
		"""language must be one the project has a runner for: c, cpp or python."""
		with self.assertRaisesRegex(ExerciseError, "rust"):
			make_exercise(language="rust")
