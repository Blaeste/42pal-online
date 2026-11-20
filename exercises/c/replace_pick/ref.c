/*
** Reference solution of replace_pick (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LAST -DMATCH_ANY_CASE ref.c
*/

#include <unistd.h>

#if !defined(WHICH_FIRST) && !defined(WHICH_LAST) && !defined(WHICH_EVERY_OTHER) \
	&& !defined(WHICH_ALL_BUT_FIRST)
# error "choose which: -DWHICH_FIRST, -DWHICH_LAST, -DWHICH_EVERY_OTHER or -DWHICH_ALL_BUT_FIRST"
#endif

#if !defined(MATCH_EXACT) && !defined(MATCH_ANY_CASE)
# error "choose a match: -DMATCH_EXACT or -DMATCH_ANY_CASE"
#endif

static int	found(char c, char find)
{
#if defined(MATCH_ANY_CASE)
	if (c >= 'A' && c <= 'Z')
		c = c - 'A' + 'a';
	if (find >= 'A' && find <= 'Z')
		find = find - 'A' + 'a';
#endif
	return (c == find);
}

int	main(int ac, char **av)
{
	int	i;
	int	count;
	int	total;

	if (ac == 4 && av[2][0] && !av[2][1] && av[3][0] && !av[3][1])
	{
		total = 0;
		i = -1;
		while (av[1][++i])
			total += found(av[1][i], av[2][0]);
		(void)total;
		count = 0;
		i = -1;
		while (av[1][++i])
		{
			if (found(av[1][i], av[2][0]))
			{
#if defined(WHICH_FIRST)
				if (count == 0)
#elif defined(WHICH_LAST)
				if (count == total - 1)
#elif defined(WHICH_EVERY_OTHER)
				if (count % 2 == 0)
#else
				if (count > 0)
#endif
					av[1][i] = av[3][0];
				count++;
			}
		}
		write(1, av[1], i);
	}
	write(1, "\n", 1);
	return (0);
}
