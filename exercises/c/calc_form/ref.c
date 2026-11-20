/*
** Reference solution of calc_form (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DORDER_PREFIX -DOPERATORS_WORDS -DSHOW_EQUATION ref.c
*/

#include <stdlib.h>
#include <unistd.h>

/* Where the operation and the two numbers are in av. */
#if defined(ORDER_INFIX)
# define A 1
# define OP 2
# define B 3
#elif defined(ORDER_PREFIX)
# define OP 1
# define A 2
# define B 3
#elif defined(ORDER_POSTFIX)
# define A 1
# define B 2
# define OP 3
#else
# error "choose an order: -DORDER_INFIX, -DORDER_PREFIX or -DORDER_POSTFIX"
#endif

#if !defined(OPERATORS_SYMBOLS) && !defined(OPERATORS_WORDS)
# error "choose the operators: -DOPERATORS_SYMBOLS or -DOPERATORS_WORDS"
#endif

#if !defined(SHOW_RESULT) && !defined(SHOW_EQUATION)
# error "choose what to show: -DSHOW_RESULT or -DSHOW_EQUATION"
#endif

static int	same(char *a, char *b)
{
	while (*a && *a == *b)
	{
		a++;
		b++;
	}
	return (*a == *b);
}

#if defined(SHOW_EQUATION)

static void	put_str(char *text)
{
	while (*text)
		write(1, text++, 1);
}

#endif

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

/* The index of the operation among +, -, *, / and % (or their words). */
static int	kind_of(char *operation)
{
	/* static: a table in the program, not filled at each call (with memset). */
#if defined(OPERATORS_SYMBOLS)
	static char	*names[5] = {"+", "-", "*", "/", "%"};
#else
	static char	*names[5] = {"plus", "minus", "times", "over", "mod"};
#endif
	int		kind;

	kind = 0;
	while (kind < 5 && !same(operation, names[kind]))
		kind++;
	return (kind);
}

int	main(int ac, char **av)
{
	int	a;
	int	b;
	int	kind;
	int	result;

	if (ac == 4)
	{
		a = atoi(av[A]);
		b = atoi(av[B]);
		kind = kind_of(av[OP]);
		result = a + b;
		if (kind == 1)
			result = a - b;
		else if (kind == 2)
			result = a * b;
		else if (kind == 3)
			result = a / b;
		else if (kind == 4)
			result = a % b;
#if defined(SHOW_EQUATION)
		put_number(a);
		put_str(" ");
		put_str(av[OP]);
		put_str(" ");
		put_number(b);
		put_str(" = ");
#endif
		put_number(result);
	}
	write(1, "\n", 1);
	return (0);
}
