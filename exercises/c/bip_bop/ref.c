/*
** Reference solution of bip_bop (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DPAIR_3_4 -DUPTO_30 ref.c
*/

#include <unistd.h>

#if defined(PAIR_2_7)
# define FIRST 2
# define SECOND 7
#elif defined(PAIR_3_4)
# define FIRST 3
# define SECOND 4
#elif defined(PAIR_4_6)
# define FIRST 4
# define SECOND 6
#elif defined(PAIR_5_7)
# define FIRST 5
# define SECOND 7
#else
# error "choose a pair: -DPAIR_2_7, -DPAIR_3_4, -DPAIR_4_6 or -DPAIR_5_7"
#endif

#if defined(UPTO_30)
# define UPTO 30
#elif defined(UPTO_50)
# define UPTO 50
#else
# error "choose how far: -DUPTO_30 or -DUPTO_50"
#endif

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

int	main(int ac, char **av)
{
	int	n;

	(void)ac;
	(void)av;
	n = 1;
	while (n <= UPTO)
	{
		if (n % FIRST == 0)
			write(1, "bip", 3);
		if (n % SECOND == 0)
			write(1, "bop", 3);
		if (n % FIRST != 0 && n % SECOND != 0)
			put_number(n);
		write(1, "\n", 1);
		n++;
	}
	return (0);
}
