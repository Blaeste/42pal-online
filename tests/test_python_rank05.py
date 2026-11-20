"""Tests of the Python models of the rank 05: one per style of the real exam.

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
NAMES = ("run_pack", "path_fill", "slot_share", "loop_seek", "zone_count", "grid_seek", "word_chain")
LOADED = {name: run_path(str(EXERCISES / name / "exercise.py"))["EXERCISE"] for name in NAMES}

def result(name, params, *values):
	"""What the test main prints for the call, without its newline."""
	return LOADED[name].oracle(params, case(*values)).removesuffix("\n")

class TestRunPack(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("run_pack", {"rule": "pairs"}, "aaabcc"), "[('a', 3), ('b', 1), ('c', 2)]")
		self.assertEqual(result("run_pack", {"rule": "pairs"}, ""), "[]")
		self.assertEqual(result("run_pack", {"rule": "count_first"}, "aaabcc"), "'3ab2c'")
		self.assertEqual(result("run_pack", {"rule": "count_first"}, "z" * 12), "'12z'")
		self.assertEqual(result("run_pack", {"rule": "expand"}, "3ab2c"), "'aaabcc'")
		self.assertEqual(result("run_pack", {"rule": "expand"}, "12z"), repr("z" * 12))
		self.assertEqual(result("run_pack", {"rule": "expand"}, ""), "''")

class TestPathFill(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("path_fill", {"rule": "counter"}, 3), "[[1, 8, 7], [2, 9, 6], [3, 4, 5]]")
		self.assertEqual(result("path_fill", {"rule": "counter"}, 0), "[]")
		self.assertEqual(result("path_fill", {"rule": "snake"}, 2, 3), "[[1, 2, 3], [6, 5, 4]]")
		self.assertEqual(result("path_fill", {"rule": "rect_spiral"}, 3, 4),
			"[[1, 2, 3, 4], [10, 11, 12, 5], [9, 8, 7, 6]]")

class TestSlotShare(unittest.TestCase):
	MEETINGS = [[1, 3], [2, 6], [8, 10], [10, 12], [15, 18]]

	def test_each_rule(self):
		self.assertEqual(result("slot_share", {"rule": "merge"}, self.MEETINGS), "[[1, 6], [8, 12], [15, 18]]")
		self.assertEqual(result("slot_share", {"rule": "gaps"}, self.MEETINGS, 0, 16),
			"[[0, 1], [6, 8], [12, 15]]")
		self.assertEqual(result("slot_share", {"rule": "busiest"}, self.MEETINGS), "[2, 2]")
		self.assertEqual(result("slot_share", {"rule": "busiest"}, [[1, 3], [3, 5]]), "[1, 1]")
		self.assertEqual(result("slot_share", {"rule": "busiest"}, []), "[0, 0]")

class TestLoopSeek(unittest.TestCase):
	GRAPH = {1: [2], 2: [3], 3: [1, 4], 4: [], 5: [5]}

	def test_each_rule(self):
		self.assertEqual(result("loop_seek", {"rule": "find"}, self.GRAPH), "[1, 2, 3]")
		self.assertEqual(result("loop_seek", {"rule": "find"}, {5: [5]}), "[5]")
		self.assertEqual(result("loop_seek", {"rule": "find"}, {1: [2], 2: [3], 3: []}), "None")
		self.assertEqual(result("loop_seek", {"rule": "on_cycle"}, self.GRAPH), "[1, 2, 3, 5]")
		self.assertEqual(result("loop_seek", {"rule": "undirected"}, {1: [2], 2: [1, 3], 3: [2]}), "False")
		self.assertEqual(result("loop_seek", {"rule": "undirected"}, {1: [2, 3], 2: [1, 3], 3: [1, 2]}),
			"True")
		self.assertEqual(result("loop_seek", {"rule": "undirected"}, {1: [1]}), "True")

class TestZoneCount(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("zone_count", {"rule": "largest"}, ["##..", "#..#", "..##", "#..."]), "3")
		self.assertEqual(result("zone_count", {"rule": "diagonal"}, ["#.#", ".#.", "#.."]), "1")
		self.assertEqual(result("zone_count", {"rule": "largest"}, ["#.#", ".#.", "#.."]), "1")
		self.assertEqual(result("zone_count", {"rule": "lakes"}, ["#####", "#..##", "#####", "#.#.#"]), "1")
		self.assertEqual(result("zone_count", {"rule": "perimeter"}, ["##", "#."]), "8")
		self.assertEqual(result("zone_count", {"rule": "perimeter"}, ["#"]), "4")

class TestGridSeek(unittest.TestCase):
	GRID = ["cat", "aox", "tac"]

	def test_each_rule(self):
		self.assertEqual(result("grid_seek", {"rule": "first"}, self.GRID, "cat"), "(0, 0, 'R')")
		self.assertEqual(result("grid_seek", {"rule": "first"}, self.GRID, "tac"), "(0, 2, 'L')")
		self.assertEqual(result("grid_seek", {"rule": "first"}, self.GRID, "xyz"), "None")
		self.assertEqual(result("grid_seek", {"rule": "straight"}, self.GRID, "cat"), "3")
		self.assertEqual(result("grid_seek", {"rule": "path"}, self.GRID, "cao"), "True")
		self.assertEqual(result("grid_seek", {"rule": "path"}, self.GRID, "cac"), "False")

class TestWordChain(unittest.TestCase):
	WORDS = ["hot", "dot", "dog", "lot", "log", "cog"]

	def test_each_rule(self):
		self.assertEqual(result("word_chain", {"rule": "path"}, "hit", "cog", self.WORDS),
			"['hit', 'hot', 'dot', 'dog', 'cog']")
		self.assertEqual(result("word_chain", {"rule": "path"}, "hit", "cog", ["hot"]), "None")
		self.assertEqual(result("word_chain", {"rule": "reachable"}, "hit", self.WORDS), "6")
		self.assertEqual(result("word_chain", {"rule": "grow"}, "a", "abc", ["ab", "abc", "b"]), "3")
		self.assertEqual(result("word_chain", {"rule": "grow"}, "cat", "cot", ["cot"]), "2")
		self.assertEqual(result("word_chain", {"rule": "grow"}, "cat", "dog", ["dog"]), "0")

class TestSubjects(unittest.TestCase):
	def test_every_variant_renders_within_80_columns(self):
		for name, exercise in LOADED.items():
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line.expandtabs(4)), 80, f"{name} {params}: {line}")
