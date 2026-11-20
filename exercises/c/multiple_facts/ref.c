/*
** Reference solution of multiple_facts (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_FIRST_THREE ref.c
*/

#include <unistd.h>

#if !defined(WHAT_LCM_ALL) && !defined(WHAT_FIRST_THREE) && !defined(WHAT_COUNT_UP_TO_1000) \
	&& !defined(WHAT_NEXT_AFTER_100)
# error "choose what: -DWHAT_LCM_ALL, -DWHAT_FIRST_THREE, -DWHAT_COUNT_UP_TO_1000 \
or -DWHAT_NEXT_AFTER_100"
#endif

typedef unsigned long long	t_big;

static void	put_number(t_big n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

/* The number in str: digits only, from 1 to 1000; or 0. */
static t_big	read_number(char *str)
{
	t_big	n;

	n = 0;
	if (!*str)
		return (0);
	while (*str)
	{
		if (*str < '0' || *str > '9' || n > 1000)
			return (0);
		n = n * 10 + (*str++ - '0');
	}
	return (n <= 1000 ? n : 0);
}

static t_big	gcd(t_big a, t_big b)
{
	t_big	r;

	while (b)
	{
		r = a % b;
		a = b;
		b = r;
	}
	return (a);
}

int	main(int ac, char **av)
{
	t_big	lcm;
	t_big	n;
	int		i;

	lcm = 1;
	i = 1;
	while (ac >= 3 && ac <= 6 && i < ac && (n = read_number(av[i])) > 0)
	{
		lcm = lcm / gcd(lcm, n) * n;
		i++;
	}
	if (ac >= 3 && ac <= 6 && i == ac)
	{
#if defined(WHAT_LCM_ALL)
		put_number(lcm);
#elif defined(WHAT_FIRST_THREE)
		put_number(lcm);
		write(1, " ", 1);
		put_number(2 * lcm);
		write(1, " ", 1);
		put_number(3 * lcm);
#elif defined(WHAT_COUNT_UP_TO_1000)
		put_number(1000 / lcm);
#else
		put_number((100 / lcm + 1) * lcm);
#endif
	}
	write(1, "\n", 1);
	return (0);
}
