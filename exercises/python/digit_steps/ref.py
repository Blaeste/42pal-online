"""Reference solution of digit_steps, for every variant: one function each."""

def _count(text, good):
	count = 0
	for index in range(len(text) - 1):
		a, b = text[index], text[index + 1]
		if "0" <= a <= "9" and "0" <= b <= "9" and good(ord(a) - 48, ord(b) - 48):
			count += 1
	return count

def steps_down(text):
	return _count(text, lambda a, b: a - b == 1)

def steps_equal(text):
	return _count(text, lambda a, b: a == b)

def steps_wrap_up(text):
	return _count(text, lambda a, b: b - a == 1 or (a == 9 and b == 0))

def steps_longest_run(text):
	best = 0
	run = 0
	previous = None
	for char in text:
		if "0" <= char <= "9":
			digit = ord(char) - 48
			if previous is not None and digit == previous + 1:
				run += 1
			else:
				run = 1
			previous = digit
			if run > best:
				best = run
		else:
			run = 0
			previous = None
	return best
