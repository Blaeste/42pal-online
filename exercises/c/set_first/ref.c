/*
** Reference solution of set_first (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSET_DIGIT -DFALLBACK_DASH ref.c
*/

#include <unistd.h>

#if defined(SET_VOWEL)
# define SET "aeiouAEIOU"
#elif defined(SET_DIGIT)
# define SET "0123456789"
#elif defined(SET_UPPER)
# define SET "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#elif defined(SET_PUNCT)
# define SET ".,;:!?"
#else
# error "choose a set: -DSET_VOWEL, -DSET_DIGIT, -DSET_UPPER or -DSET_PUNCT"
#endif

#if defined(FALLBACK_QUESTION)
# define FALLBACK "?"
#elif defined(FALLBACK_DASH)
# define FALLBACK "-"
#else
# error "choose a fallback: -DFALLBACK_QUESTION or -DFALLBACK_DASH"
#endif

static int	in_set(char c)
{
	char	*set;

	set = SET;
	while (*set)
		if (*set++ == c)
			return (1);
	return (0);
}

int	main(int ac, char **av)
{
	int	i;

	i = 0;
	while (ac == 2 && av[1][i] && !in_set(av[1][i]))
		i++;
	if (ac == 2 && av[1][i])
		write(1, &av[1][i], 1);
	else
		write(1, FALLBACK, 1);
	write(1, "\n", 1);
	return (0);
}
