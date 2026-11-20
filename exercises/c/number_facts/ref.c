/*
** Reference solution of number_facts, for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_DIVISORS -DSEPARATOR_COMMA ref.c
*/

#include <unistd.h>

#if !defined(WHAT_DIVISORS) && !defined(WHAT_PRIME_DIVISORS) && !defined(WHAT_PRIMES_UP_TO)
# error "choose a list: -DWHAT_DIVISORS, -DWHAT_PRIME_DIVISORS or -DWHAT_PRIMES_UP_TO"
#endif

#if defined(SEPARATOR_SPACE)
# define SEPARATOR " "
#elif defined(SEPARATOR_COMMA)
# define SEPARATOR ", "
#elif defined(SEPARATOR_NEWLINE)
# define SEPARATOR "\n"
#else
# error "choose a separator: -DSEPARATOR_SPACE, _COMMA or _NEWLINE"
#endif

/* The number written in s, or 0 if s is not 1 to 6 digits only. */
static int	read_number(char *s)
{
	int	n;
	int	i;

	n = 0;
	i = 0;
	while (s[i] >= '0' && s[i] <= '9' && i < 7)
		n = n * 10 + s[i++] - '0';
	if (i == 0 || i > 6 || s[i])
		return (0);
	return (n);
}

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = n % 10 + '0';
	write(1, &digit, 1);
}

#if !defined(WHAT_DIVISORS)

static int	is_prime(int n)
{
	int	d;

	if (n < 2)
		return (0);
	d = 2;
	while (d * d <= n)
	{
		if (n % d == 0)
			return (0);
		d++;
	}
	return (1);
}

#endif

/* True when d belongs to the list asked for, about n. */
static int	in_list(int d, int n)
{
#if defined(WHAT_DIVISORS)
	return (n % d == 0);
#elif defined(WHAT_PRIME_DIVISORS)
	return (n % d == 0 && is_prime(d));
#else
	(void)n;
	return (is_prime(d));
#endif
}

int	main(int ac, char **av)
{
	int	n;
	int	d;
	int	first;

	n = 0;
	if (ac == 2)
		n = read_number(av[1]);
	first = 1;
	d = 1;
	while (d <= n)
	{
		if (in_list(d, n))
		{
			if (!first)
				write(1, SEPARATOR, sizeof(SEPARATOR) - 1);
			put_number(d);
			first = 0;
		}
		d++;
	}
	write(1, "\n", 1);
	return (0);
}
