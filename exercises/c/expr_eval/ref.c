/*
** Reference solution of expr_eval (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DNOTATION_NESTED ref.c
*/

#include <unistd.h>

#if !defined(NOTATION_PREFIX) && !defined(NOTATION_COMPACT) && !defined(NOTATION_NESTED)
# error "choose a notation: -DNOTATION_PREFIX, -DNOTATION_COMPACT or -DNOTATION_NESTED"
#endif

static int	is_operator(char c)
{
	return (c == '+' || c == '-' || c == '*' || c == '/' || c == '%');
}

static int	is_digit(char c)
{
	return (c >= '0' && c <= '9');
}

/* left operator right in *result; 0 for a division by 0. */
static int	apply(char operator, int left, int right, int *result)
{
	if ((operator == '/' || operator == '%') && right == 0)
		return (0);
	if (operator == '+')
		*result = left + right;
	else if (operator == '-')
		*result = left - right;
	else if (operator == '*')
		*result = left * right;
	else if (operator == '/')
		*result = left / right;
	else
		*result = left % right;
	return (1);
}

static void	put_number(long n)
{
	char	digit;

	if (n < 0)
	{
		write(1, "-", 1);
		n = -n;
	}
	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

#if defined(NOTATION_PREFIX)

/* The tokens from the last one: a number is pushed, an operator takes two. */
static int	compute(char *s, int *result)
{
	int	stack[1000];
	int	size;
	int	end;
	int	start;
	int	i;

	size = 0;
	end = 0;
	while (s[end])
		end++;
	while (end > 0)
	{
		while (end > 0 && s[end - 1] == ' ')
			end--;
		start = end;
		while (start > 0 && s[start - 1] != ' ')
			start--;
		if (start == end)
			break ;
		if (end - start == 1 && is_operator(s[start]))
		{
			if (size < 2 || !apply(s[start], stack[size - 1], stack[size - 2], &stack[size - 2]))
				return (0);
			size--;
		}
		else
		{
			stack[size] = 0;
			i = start;
			while (i < end)
			{
				if (!is_digit(s[i]))
					return (0);
				stack[size] = stack[size] * 10 + s[i++] - '0';
			}
			size++;
		}
		end = start;
	}
	*result = stack[0];
	return (size == 1);
}

#elif defined(NOTATION_COMPACT)

/* The characters from the first one: a digit is pushed, an operator takes two. */
static int	compute(char *s, int *result)
{
	int	stack[1000];
	int	size;

	size = 0;
	while (*s)
	{
		if (is_operator(*s))
		{
			if (size < 2 || !apply(*s, stack[size - 2], stack[size - 1], &stack[size - 2]))
				return (0);
			size--;
		}
		else if (is_digit(*s))
			stack[size++] = *s - '0';
		else
			return (0);
		s++;
	}
	*result = stack[0];
	return (size == 1);
}

#else

/* An expression from s[*at]: a number, or ( expression operator expression ). */
static int	expression(char *s, int *at, int *result)
{
	int		left;
	int		right;
	char	operator;

	if (s[*at] == '(')
	{
		(*at)++;
		if (!expression(s, at, &left) || !is_operator(s[*at]))
			return (0);
		operator = s[(*at)++];
		if (!expression(s, at, &right) || s[*at] != ')')
			return (0);
		(*at)++;
		return (apply(operator, left, right, result));
	}
	if (!is_digit(s[*at]))
		return (0);
	*result = 0;
	while (is_digit(s[*at]))
		*result = *result * 10 + s[(*at)++] - '0';
	return (1);
}

static int	compute(char *s, int *result)
{
	int	at;

	at = 0;
	return (expression(s, &at, result) && s[at] == '\0');
}

#endif

int	main(int ac, char **av)
{
	int	value;

	if (ac != 2)
		return (write(1, "\n", 1), 0);
	if (!compute(av[1], &value))
		return (write(1, "Error\n", 6), 0);
	put_number(value);
	write(1, "\n", 1);
	return (0);
}
