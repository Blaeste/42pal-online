"""Tests of the Python models of the rank 06: one per style of the real exam.

Each test calls the oracle of a variant on values chosen by hand; the
expected results are worked out by hand, never by the oracle. A class is
tested with the arguments of its constructor and a list of calls.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path
from runpy import run_path

from pal42.python_exercise import case, class_case
from pal42.subject import render
from pal42.variant import Variant

EXERCISES = Path(__file__).resolve().parent.parent / "exercises/python"
NAMES = ("word_tree", "string_pack", "task_plan", "edge_spare", "word_complete", "set_groups",
	"value_keeper", "top_heap", "cut_find")
LOADED = {name: run_path(str(EXERCISES / name / "exercise.py"))["EXERCISE"] for name in NAMES}

def result(name, params, *values):
	"""What the test main prints for the call, without its newline."""
	return LOADED[name].oracle(params, case(*values)).removesuffix("\n")

def calls(name, params, init, steps):
	"""What the test main of a class prints for these calls, without its newline."""
	return LOADED[name].oracle(params, class_case(init, steps)).removesuffix("\n")

class TestWordTree(unittest.TestCase):
	def test_count(self):
		steps = [["add", "car"], ["add", "cat"], ["add", "car"], ["count", "ca"], ["count", "car"],
			["remove", "car"], ["count", "car"], ["remove", "dog"], ["count", ""]]
		self.assertEqual(calls("word_tree", {"rule": "count"}, [], steps),
			"[None, None, None, 3, 2, True, 1, False, 2]")

	def test_longest(self):
		steps = [["add", "a"], ["add", "app"], ["add", "apple"], ["longest", "applesauce"],
			["longest", "apricot"], ["longest", "banana"]]
		self.assertEqual(calls("word_tree", {"rule": "longest"}, [], steps),
			"[None, None, None, 'apple', 'a', '']")

	def test_pattern(self):
		steps = [["add", "bad"], ["add", "dad"], ["match", "b.d"], ["match", ".a."], ["match", "...."],
			["match", "c.d"]]
		self.assertEqual(calls("word_tree", {"rule": "pattern"}, [], steps),
			"[None, None, True, True, False, False]")

class TestStringPack(unittest.TestCase):
	def test_escape(self):
		self.assertEqual(result("string_pack", {"rule": "pack_escape"}, []), "''")
		self.assertEqual(result("string_pack", {"rule": "pack_escape"}, [""]), "';'")
		self.assertEqual(result("string_pack", {"rule": "pack_escape"}, ["a;b", "c\\"]), repr("a\\;b;c\\\\;"))
		self.assertEqual(result("string_pack", {"rule": "unpack_escape"}, "a\\;b;c\\\\;"), repr(["a;b", "c\\"]))
		self.assertEqual(result("string_pack", {"rule": "unpack_escape"}, "abc"), "None")
		self.assertEqual(result("string_pack", {"rule": "unpack_escape"}, "a\\x;"), "None")
		self.assertEqual(result("string_pack", {"rule": "unpack_escape"}, ""), "[]")
		self.assertEqual(result("string_pack", {"rule": "unpack_escape"}, ";;"), "['', '']")

	def test_length(self):
		self.assertEqual(result("string_pack", {"rule": "unpack_length"}, "3:abc0:2:de"), "['abc', '', 'de']")
		self.assertEqual(result("string_pack", {"rule": "unpack_length"}, "3:ab"), "None")
		self.assertEqual(result("string_pack", {"rule": "unpack_length"}, "x:a"), "None")
		self.assertEqual(result("string_pack", {"rule": "unpack_length"}, ""), "[]")

class TestTaskPlan(unittest.TestCase):
	PREREQS = [[1, 0], [2, 0], [3, 1], [3, 2]]

	def test_each_rule(self):
		self.assertEqual(result("task_plan", {"rule": "rounds"}, 4, self.PREREQS), "3")
		self.assertEqual(result("task_plan", {"rule": "rounds"}, 2, [[0, 1], [1, 0]]), "-1")
		self.assertEqual(result("task_plan", {"rule": "rounds"}, 0, []), "0")
		self.assertEqual(result("task_plan", {"rule": "rounds"}, 3, []), "1")
		self.assertEqual(result("task_plan", {"rule": "ancestors"}, 4, self.PREREQS, 3), "[0, 1, 2]")
		self.assertEqual(result("task_plan", {"rule": "ancestors"}, 4, self.PREREQS, 0), "[]")
		self.assertEqual(result("task_plan", {"rule": "largest_first"}, 4, self.PREREQS), "[0, 2, 1, 3]")
		self.assertEqual(result("task_plan", {"rule": "largest_first"}, 2, [[0, 1], [1, 0]]), "[]")

class TestEdgeSpare(unittest.TestCase):
	def test_each_rule(self):
		self.assertEqual(result("edge_spare", {"rule": "components"}, 5, [[1, 2], [3, 4]]), "3")
		self.assertEqual(result("edge_spare", {"rule": "cycle_edges"}, [[1, 2], [2, 3], [3, 4], [4, 2], [1, 5]]),
			"[[2, 3], [3, 4], [4, 2]]")
		self.assertEqual(result("edge_spare", {"rule": "count"}, 4, [[1, 2], [2, 3], [3, 1], [1, 4], [2, 4]]),
			"2")

class TestWordComplete(unittest.TestCase):
	def test_each_rule(self):
		words = ["car", "cat", "car", "cart", "dog", "cat", "car"]
		self.assertEqual(result("word_complete", {"rule": "top_k"}, words, "ca", 2), "['car', 'cat']")
		self.assertEqual(result("word_complete", {"rule": "next_letters"}, ["car", "cat", "cart", "ca", "dog"],
			"ca"), "'rt'")
		self.assertEqual(result("word_complete", {"rule": "shortest_unique"}, ["dog", "cat", "car", "cart"]),
			"['d', 'cat', 'car', 'cart']")

class TestSetGroups(unittest.TestCase):
	def test_sizes(self):
		steps = [["union", 0, 1], ["union", 1, 2], ["union", 0, 2], ["size", 2], ["size", 4], ["count"]]
		self.assertEqual(calls("set_groups", {"rule": "sizes"}, [5], steps), "[True, True, False, 3, 1, 3]")

	def test_names(self):
		steps = [["join", "ann", "bob"], ["join", "cid", "dan"], ["same", "ann", "dan"], ["join", "bob", "dan"],
			["members", "cid"], ["same", "eve", "eve"], ["members", "eve"]]
		self.assertEqual(calls("set_groups", {"rule": "names"}, [], steps),
			"[True, True, False, True, ['ann', 'bob', 'cid', 'dan'], True, ['eve']]")

	def test_undo(self):
		steps = [["union", 0, 1], ["union", 2, 3], ["union", 0, 1], ["together", 0, 3], ["union", 1, 3],
			["together", 0, 2], ["undo"], ["together", 0, 2], ["together", 2, 3], ["undo"], ["undo"], ["undo"],
			["together", 0, 1]]
		self.assertEqual(calls("set_groups", {"rule": "undo"}, [4], steps),
			"[True, True, False, False, True, True, True, False, True, True, True, False, False]")

class TestValueKeeper(unittest.TestCase):
	def test_lfu(self):
		steps = [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 2], ["get", 3], ["put", 4, 4],
			["get", 1], ["get", 3], ["get", 4]]
		self.assertEqual(calls("value_keeper", {"rule": "lfu"}, [2], steps),
			"[None, None, 1, None, -1, 3, None, -1, 3, 4]")

	def test_fifo(self):
		steps = [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 1], ["put", 2, 20],
			["put", 4, 4], ["get", 2], ["get", 3]]
		self.assertEqual(calls("value_keeper", {"rule": "fifo"}, [2], steps),
			"[None, None, 1, None, -1, None, None, -1, 3]")

	def test_mru(self):
		steps = [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 1], ["get", 2], ["get", 3],
			["put", 4, 4], ["get", 2]]
		self.assertEqual(calls("value_keeper", {"rule": "mru"}, [2], steps),
			"[None, None, 1, None, -1, 2, 3, None, 2]")

class TestTopHeap(unittest.TestCase):
	def test_each_rule(self):
		steps = [["push", 3], ["push", 9], ["push", 1], ["peek"], ["pop"], ["size"], ["pop"], ["pop"], ["pop"],
			["peek"]]
		self.assertEqual(calls("top_heap", {"rule": "max_heap"}, [], steps),
			"[None, None, None, 9, 9, 2, 3, 1, None, None]")
		steps = [["kth"], ["add", 5], ["kth"], ["add", 1], ["kth"], ["add", 8], ["kth"], ["add", 8], ["kth"]]
		self.assertEqual(calls("top_heap", {"rule": "k_largest"}, [2], steps),
			"[None, None, None, None, 1, None, 5, None, 8]")
		steps = [["median"], ["add", 5], ["median"], ["add", 1], ["median"], ["add", 9], ["median"], ["add", 3],
			["median"]]
		self.assertEqual(calls("top_heap", {"rule": "median"}, [], steps),
			"[None, None, 5, None, 1, None, 5, None, 3]")

class TestCutFind(unittest.TestCase):
	GRAPH = {1: [2], 2: [1, 3, 4], 3: [2, 4], 4: [2, 3, 5], 5: [4]}

	def test_each_rule(self):
		self.assertEqual(result("cut_find", {"rule": "points"}, self.GRAPH), "[2, 4]")
		self.assertEqual(result("cut_find", {"rule": "groups"}, self.GRAPH), "{1: 1, 2: 2, 3: 1, 4: 2, 5: 1}")

class TestSubjects(unittest.TestCase):
	def test_every_variant_renders_within_80_columns(self):
		for name, exercise in LOADED.items():
			for params in exercise.combinations():
				for line in render(Variant(exercise, 0, params)).splitlines():
					self.assertLessEqual(len(line.expandtabs(4)), 80, f"{name} {params}: {line}")
