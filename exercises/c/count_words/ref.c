/*
** Reference solution of count_words (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DBIP_BY3 -DBOP_HAS7 ref.c
*/

#include <unistd.h>

#if defined(BIP_BY3)
# define BIP 3
#elif defined(BIP_BY4)
# define BIP 4
#else
# error "choose bip: -DBIP_BY3 or -DBIP_BY4"
#endif

#if !defined(BOP_HAS7) && !defined(BOP_HAS2) && !defined(BOP_ENDS5)
# error "choose bop: -DBOP_HAS7, -DBOP_HAS2 or -DBOP_ENDS5"
#endif

static int	is_bop(int n)
{
#if defined(BOP_ENDS5)
	return (n % 10 == 5);
#else
# if defined(BOP_HAS7)
	int	digit = 7;
# else
	int	digit = 2;
# endif

	while (n > 0)
	{
		if (n % 10 == digit)
			return (1);
		n /= 10;
	}
	return (0);
#endif
}

static void	put_number(int n)
{
	char	c;

	if (n >= 10)
		put_number(n / 10);
	c = '0' + n % 10;
	write(1, &c, 1);
}

int	main(int ac, char **av)
{
	int	last;
	int	n;
	int	i;

	if (ac != 2)
		return (write(1, "\n", 1), 0);
	last = 0;
	i = 0;
	while (av[1][i] >= '0' && av[1][i] <= '9')
		last = last * 10 + av[1][i++] - '0';
	n = 0;
	while (++n <= last)
	{
		if (n % BIP == 0)
			write(1, "bip", 3);
		if (is_bop(n))
			write(1, "bop", 3);
		if (n % BIP != 0 && !is_bop(n))
			put_number(n);
		write(1, "\n", 1);
	}
	return (0);
}
