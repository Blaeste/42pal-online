"""Helpers for the Python exercises: the test main, the tests and the calls.

A Python function is graded like a C one: a test main calls it and prints
what it returns, and the grader compares that with the oracle. The values
of a test travel as Python literals in argv (repr in, ast.literal_eval
out), and the result comes back as its repr. So an exercise writes its
tests with case(), its oracle with values() and shown(), and its calls
with call():

	def oracle(params, test):
		items, steps = values(test)
		return shown(items[-steps:] + items[:-steps])

	tests = [case([1, 2, 3], 1), case([], 0)]

A class is tested the same way: class_harness() builds the object with the
arguments of the test, calls its methods one after the other and prints
the list of their results; class_case() writes such a test.
"""

import ast

from pal42.model import TestCase

# The test main of a function: MODULE and FUNCTION are replaced by harness().
# It never lets an exception out: what went wrong is printed instead, so
# that the trace shows it in place of the expected output.
HARNESS = '''"""The test main of 42pal: it calls your function and prints what it returns."""

import ast
import importlib
import sys

def main():
	try:
		module = importlib.import_module("MODULE")
	except Exception as error:
		print(f"Cannot import MODULE.py: {type(error).__name__}: {error}")
		return
	function = getattr(module, "FUNCTION", None)
	if not callable(function):
		print("MODULE.py has no function FUNCTION")
		return
	args = [ast.literal_eval(arg) for arg in sys.argv[1:]]
	try:
		result = function(*args)
	except Exception as error:
		print(f"Your function raised {type(error).__name__}: {error}")
		return
	print(repr(result))

main()
'''

def harness(module, function=None):
	"""The test main that imports `function` (by default, `module`) from module.py.

	Both may hold holes like the name of the exercise ("rotate_${side}"):
	the variant fills them in, like in a C test main.
	"""
	return HARNESS.replace("MODULE", module).replace("FUNCTION", function or module)

def case(*values):
	"""A test that calls the function with `values`, written as Python literals."""
	return TestCase(tuple(repr(value) for value in values))

def values(test):
	"""The values of a test, read back from its literals."""
	return [ast.literal_eval(arg) for arg in test.args]

def call(name, test):
	"""The call of the function `name` on `test`, as the examples and traces show it."""
	return f"{name}({', '.join(test.args)})"

def shown(result):
	"""What the test main prints for `result`: its repr, then a newline."""
	return f"{result!r}\n"

# The test main of a class: the test gives the arguments of the constructor
# and a list of calls [method, arg...]; it prints the list of their results.
# CLASS_NAME and MODULE are replaced by class_harness().
CLASS_HARNESS = '''"""The test main of 42pal: it builds your object, calls its methods, prints the results."""

import ast
import importlib
import sys

def main():
	try:
		module = importlib.import_module("MODULE")
	except Exception as error:
		print(f"Cannot import MODULE.py: {type(error).__name__}: {error}")
		return
	cls = getattr(module, "CLASS_NAME", None)
	if not isinstance(cls, type):
		print("MODULE.py has no class CLASS_NAME")
		return
	init, calls = (ast.literal_eval(arg) for arg in sys.argv[1:3])
	try:
		obj = cls(*init)
	except Exception as error:
		print(f"CLASS_NAME() raised {type(error).__name__}: {error}")
		return
	results = []
	for number, (name, *args) in enumerate(calls, start=1):
		method = getattr(obj, name, None)
		if not callable(method):
			print(f"CLASS_NAME has no method {name} (call {number})")
			return
		try:
			results.append(method(*args))
		except Exception as error:
			print(f"{name}() raised {type(error).__name__}: {error} (call {number})")
			return
	print(repr(results))

main()
'''

def class_harness(module, class_name):
	"""The test main that builds a `class_name` from module.py and calls its methods."""
	return CLASS_HARNESS.replace("MODULE", module).replace("CLASS_NAME", class_name)

def class_case(init, calls):
	"""A test of a class: the arguments of its constructor, then the calls [method, arg...]."""
	return case(list(init), [list(one) for one in calls])

def class_values(test):
	"""The constructor arguments and the calls of a class test, read back."""
	init, calls = values(test)
	return init, calls

def class_call(class_name):
	"""How the examples and traces show a class test: o = Name(...); [o.m(...), ...]."""
	def shown_call(name, test):
		init, calls = class_values(test)
		made = ", ".join(map(repr, init))
		done = ", ".join(f"o.{method}({', '.join(map(repr, args))})" for method, *args in calls)
		return f"o = {class_name}({made}); [{done}]"
	return shown_call
