/*
** Reference solution of arg_pick, for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LONGEST -DCASE_UPPER ref.c
*/

#include <unistd.h>

#if !defined(WHICH_FIRST) && !defined(WHICH_LAST) && !defined(WHICH_LONGEST) \
	&& !defined(WHICH_SHORTEST)
# error "choose an argument: -DWHICH_FIRST, _LAST, _LONGEST or _SHORTEST"
#endif
#if !defined(CASE_AS_IS) && !defined(CASE_UPPER)
# error "choose a case: -DCASE_AS_IS or -DCASE_UPPER"
#endif

#if defined(WHICH_LONGEST) || defined(WHICH_SHORTEST)

static int	length(char *s)
{
	int	n;

	n = 0;
	while (s[n])
		n++;
	return (n);
}

#endif

/* The index of the argument to print, among av[1] to av[ac - 1]. */
static int	pick(int ac, char **av)
{
	int	chosen;
	int	i;

	/* first and last do not look at every argument: ac, av or i may be unused. */
	(void)ac;
	(void)av;
	chosen = 1;
#if defined(WHICH_LAST)
	chosen = ac - 1;
#elif defined(WHICH_LONGEST) || defined(WHICH_SHORTEST)
	i = 2;
	while (i < ac)
	{
# if defined(WHICH_LONGEST)
		if (length(av[i]) > length(av[chosen]))
# else
		if (length(av[i]) < length(av[chosen]))
# endif
			chosen = i;
		i++;
	}
#endif
	(void)i;
	return (chosen);
}

int	main(int ac, char **av)
{
	char	*s;

	if (ac > 1)
	{
		s = av[pick(ac, av)];
		while (*s)
		{
#if defined(CASE_UPPER)
			if (*s >= 'a' && *s <= 'z')
				*s = *s - 'a' + 'A';
#endif
			write(1, s, 1);
			s++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
