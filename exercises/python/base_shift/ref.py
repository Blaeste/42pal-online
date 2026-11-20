"""Reference solution of base_shift, for every variant: one function each."""

SYMBOLS = "0123456789abcdefghijklmnopqrstuvwxyz"

def _value(number, base):
	if base < 2 or base > 36:
		return None
	sign = 1
	if number[:1] == "-":
		sign = -1
		number = number[1:]
	if number == "":
		return None
	value = 0
	for char in number.lower():
		digit = SYMBOLS.find(char)
		if digit < 0 or digit >= base:
			return None
		value = value * base + digit
	return sign * value

def _written(value, base):
	if value == 0:
		return "0"
	sign = "-" if value < 0 else ""
	value = abs(value)
	digits = []
	while value > 0:
		digits.append(SYMBOLS[value % base].upper())
		value //= base
	return sign + "".join(reversed(digits))

def base_to_decimal(number, base):
	value = _value(number, base)
	return None if value is None else str(value)

def base_from_decimal(number, base):
	if base < 2 or base > 36:
		return None
	value = _value(number, 10)
	return None if value is None else _written(value, base)

def base_next(number, base):
	value = _value(number, base)
	return None if value is None else _written(value + 1, base)
