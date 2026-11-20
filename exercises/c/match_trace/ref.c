/*
** Reference solution of match_trace (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_MARKED -DCASE_ANY_CASE ref.c
*/

#include <unistd.h>

#if !defined(WHAT_MARKED) && !defined(WHAT_SKIPPED) && !defined(WHAT_PREFIX)
# error "choose what: -DWHAT_MARKED, -DWHAT_SKIPPED or -DWHAT_PREFIX"
#endif

#if !defined(CASE_EXACT) && !defined(CASE_ANY_CASE)
# error "choose the case: -DCASE_EXACT or -DCASE_ANY_CASE"
#endif

static int	same(char a, char b)
{
#if defined(CASE_ANY_CASE)
	if (a >= 'A' && a <= 'Z')
		a = a - 'A' + 'a';
	if (b >= 'A' && b <= 'Z')
		b = b - 'A' + 'a';
#endif
	return (a == b);
}

int	main(int ac, char **av)
{
	char	used[4096];
	char	c;
	int		made;
	int		i;
	int		j;

	if (ac == 3)
	{
		i = -1;
		while (av[2][++i] && i < 4096)
			used[i] = 0;
		made = 0;
		j = 0;
		while (av[1][made])
		{
			while (av[2][j] && !same(av[2][j], av[1][made]))
				j++;
			if (!av[2][j])
				break ;
			used[j++] = 1;
			made++;
		}
#if defined(WHAT_PREFIX)
		(void)c;
		(void)used;
		write(1, av[1], made);
#else
		i = 0;
		while (!av[1][made] && av[2][i])
		{
			c = av[2][i];
# if defined(WHAT_MARKED)
			if (used[i] && c >= 'a' && c <= 'z')
				c = c - 'a' + 'A';
			write(1, &c, 1);
# else
			if (!used[i])
				write(1, &c, 1);
# endif
			i++;
		}
#endif
	}
	write(1, "\n", 1);
	return (0);
}
