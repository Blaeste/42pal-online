"""Tests of the Python models of the rank 04: one per style of the real exam.

Each test calls the oracle of a variant on values chosen by hand; the
expected results are worked out by hand, never by the oracle.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.python_exercise import case
from pal42.subject import render
from pal42.variant import Variant

EXERCISES = Path(__file__).resolve().parent.parent / "exercises/python"
NAMES = ("turn_find", "star_chart", "common_sorted", "merge_many", "mirror_parts", "need_order",
	"window_stat")
LOADED = {name: run_path(str(EXERCISES / name / "exercise.py"))["EXERCISE"] for name in NAMES}

def result(name, params, *values):
	"""What the test main prints for the call, without its newline."""
	return LOADED[name].oracle(params, case(*values)).removesuffix("\n")

class TestTurnFind(unittest.TestCase):
	def test_steps(self):
		self.assertEqual(result("turn_find", {"rule": "steps"}, [1, 2, 3, 4], [3, 4, 1, 2]), "2")
		self.assertEqual(result("turn_find", {"rule": "steps"}, [1, 2, 3], [3, 2, 1]), "-1")
		self.assertEqual(result("turn_find", {"rule": "steps"}, [], []), "0")

	def test_all_steps(self):
		self.assertEqual(result("turn_find", {"rule": "all_steps"}, [1, 1, 1], [1, 1, 1]), "[0, 1, 2]")
		self.assertEqual(result("turn_find", {"rule": "all_steps"}, [1, 2], [1, 2, 3]), "[]")
		self.assertEqual(result("turn_find", {"rule": "all_steps"}, [], []), "[0]")

	def test_mirrored(self):
		self.assertEqual(result("turn_find", {"rule": "mirrored"}, [1, 2, 3], [3, 2, 1]), "True")
		self.assertEqual(result("turn_find", {"rule": "mirrored"}, [1, 2, 3, 4], [2, 1, 4, 3]), "True")
		self.assertEqual(result("turn_find", {"rule": "mirrored"}, [1, 2, 3, 4], [1, 3, 2, 4]), "False")

class TestStarChart(unittest.TestCase):
	def test_count(self):
		self.assertEqual(result("star_chart", {"rule": "count"}, [(0, 0), (0, 0), (1, 2), (5, 5)], 2, 3),
			"['2..', '..1']")

	def test_bounds(self):
		self.assertEqual(result("star_chart", {"rule": "bounds"}, [(2, 3), (4, 1)]), "['..*', '...', '*..']")
		self.assertEqual(result("star_chart", {"rule": "bounds"}, []), "[]")

	def test_up(self):
		self.assertEqual(result("star_chart", {"rule": "up"}, [(0, 0), (2, 1), (3, 0)], 3),
			"['...', '..*', '*..']")

class TestCommonSorted(unittest.TestCase):
	LISTS = [[1, 2, 2, 3], [2, 2, 3, 4], [2, 3, 3, 5]]

	def test_each_rule(self):
		self.assertEqual(result("common_sorted", {"rule": "at_least"}, self.LISTS, 2), "[2, 3]")
		self.assertEqual(result("common_sorted", {"rule": "at_least"}, self.LISTS, 1), "[1, 2, 3, 4, 5]")
		self.assertEqual(result("common_sorted", {"rule": "with_counts"}, self.LISTS), "[2, 3]")
		self.assertEqual(result("common_sorted", {"rule": "with_counts"}, [[1, 1, 2], [1, 1, 1, 2, 2]]),
			"[1, 1, 2]")
		self.assertEqual(result("common_sorted", {"rule": "only_one"}, self.LISTS), "[1, 4, 5]")

class TestMergeMany(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("merge_many", {"rule": "descending"}, [[9, 1], [5, 5], []]), "[9, 5, 5, 1]")
		self.assertEqual(result("merge_many", {"rule": "first_k"}, [[1, 4], [2, 3], [1]], 3), "[1, 1, 2]")
		self.assertEqual(result("merge_many", {"rule": "first_k"}, [[1], []], 5), "[1]")
		self.assertEqual(result("merge_many", {"rule": "origins"}, [[1, 4], [2, 3], [1]]), "[0, 2, 1, 1, 0]")

class TestMirrorParts(unittest.TestCase):
	def test_ways(self):
		self.assertEqual(result("mirror_parts", {"rule": "ways"}, "aab"), "2")
		self.assertEqual(result("mirror_parts", {"rule": "ways"}, "aaa"), "4")
		self.assertEqual(result("mirror_parts", {"rule": "ways"}, ""), "1")

	def test_fewest(self):
		self.assertEqual(result("mirror_parts", {"rule": "fewest"}, "abacdc"), "['aba', 'cdc']")
		self.assertEqual(result("mirror_parts", {"rule": "fewest"}, "abab"), "['aba', 'b']")
		self.assertEqual(result("mirror_parts", {"rule": "fewest"}, ""), "[]")

	def test_no_single(self):
		self.assertEqual(result("mirror_parts", {"rule": "no_single"}, "aabb"), "2")
		self.assertEqual(result("mirror_parts", {"rule": "no_single"}, "aab"), "-1")
		self.assertEqual(result("mirror_parts", {"rule": "no_single"}, "abba"), "1")
		self.assertEqual(result("mirror_parts", {"rule": "no_single"}, ""), "0")

class TestNeedOrder(unittest.TestCase):
	PACKAGES = {"app": ["lib", "net"], "lib": ["core"], "net": ["core"], "core": [], "tool": ["x"]}
	LOOP = {"a": ["b"], "b": ["a"], "c": []}

	def test_levels(self):
		self.assertEqual(result("need_order", {"rule": "levels"}, self.PACKAGES),
			"[['core', 'tool'], ['lib', 'net'], ['app']]")
		self.assertEqual(result("need_order", {"rule": "levels"}, self.LOOP), "None")

	def test_install_for(self):
		self.assertEqual(result("need_order", {"rule": "install_for"}, self.PACKAGES, "app"),
			"['core', 'lib', 'net', 'app']")
		self.assertEqual(result("need_order", {"rule": "install_for"}, self.LOOP, "c"), "['c']")
		self.assertEqual(result("need_order", {"rule": "install_for"}, self.LOOP, "a"), "None")

	def test_depth(self):
		self.assertEqual(result("need_order", {"rule": "depth"}, self.PACKAGES),
			"{'app': 2, 'lib': 1, 'net': 1, 'core': 0, 'tool': 0}")
		self.assertEqual(result("need_order", {"rule": "depth"}, self.LOOP), "None")

class TestWindowStat(unittest.TestCase):
	NUMS = [1, 3, -1, -3, 5, 3]

	def test_each_rule(self):
		self.assertEqual(result("window_stat", {"rule": "min"}, self.NUMS, 3), "[-1, -3, -3, -3]")
		self.assertEqual(result("window_stat", {"rule": "spread"}, self.NUMS, 3), "[4, 6, 8, 8]")
		self.assertEqual(result("window_stat", {"rule": "distinct"}, [2, 2, 3, 2], 2), "[1, 2, 2]")
		self.assertEqual(result("window_stat", {"rule": "first_negative"}, self.NUMS, 3), "[-1, -1, -1, -3]")
		self.assertEqual(result("window_stat", {"rule": "min"}, [1, 2], 3), "[]")
		self.assertEqual(result("window_stat", {"rule": "min"}, [1, 2], 0), "[]")

class TestSubjects(unittest.TestCase):
	def test_every_variant_renders_within_80_columns(self):
		for name, exercise in LOADED.items():
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line.expandtabs(4)), 80, f"{name} {params}: {line}")
