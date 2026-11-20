/*
** Reference solution of op_table (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DOPERATION_POWER -DROWS_9 ref.c
*/

#include <unistd.h>

#if defined(ROWS_5)
# define ROWS 5
#elif defined(ROWS_9)
# define ROWS 9
#else
# error "choose the rows: -DROWS_5 or -DROWS_9"
#endif

#if !defined(OPERATION_PLUS) && !defined(OPERATION_MINUS) && !defined(OPERATION_POWER) \
	&& !defined(OPERATION_MODULO)
# error "choose an operation: -DOPERATION_PLUS, -DOPERATION_MINUS, -DOPERATION_POWER \
or -DOPERATION_MODULO"
#endif

static void	put_number(long long n)
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

static void	put_str(char *s)
{
	while (*s)
		write(1, s++, 1);
}

/* The number in str: digits only, from 1 to 50; or 0. */
static int	read_number(char *str)
{
	int	n;

	n = 0;
	if (!*str)
		return (0);
	while (*str)
	{
		if (*str < '0' || *str > '9' || n > 50)
			return (0);
		n = n * 10 + (*str++ - '0');
	}
	return (n <= 50 ? n : 0);
}

int	main(int ac, char **av)
{
	long long	n;
	long long	result;
	int			k;
	int			i;

	n = (ac == 2) ? read_number(av[1]) : 0;
	if (n == 0)
		write(1, "\n", 1);
	k = 1;
	while (n > 0 && k <= ROWS)
	{
		(void)i;
#if defined(OPERATION_PLUS)
		put_number(k);
		put_str(" + ");
		put_number(n);
		result = k + n;
#elif defined(OPERATION_MINUS)
		put_number(n);
		put_str(" - ");
		put_number(k);
		result = n - k;
#elif defined(OPERATION_POWER)
		put_number(n);
		put_str(" ^ ");
		put_number(k);
		result = 1;
		i = 0;
		while (i++ < k)
			result *= n;
#else
		put_number(n);
		put_str(" % ");
		put_number(k);
		result = n % k;
#endif
		put_str(" = ");
		put_number(result);
		write(1, "\n", 1);
		k++;
	}
	return (0);
}
