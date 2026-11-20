/*
** Reference solution of alpha_back (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DPATTERN_THIRDS -DSTEP_SKIP ref.c
*/

#include <unistd.h>

#if defined(STEP_ALL)
# define STEP 1
#elif defined(STEP_SKIP)
# define STEP 2
#else
# error "choose a step: -DSTEP_ALL or -DSTEP_SKIP"
#endif

/* UPPER(letter, place): true if the letter, the place-th one shown, is in uppercase. */
#if defined(PATTERN_ALTERNATE_LOWER)
# define UPPER(letter, place) ((place) % 2 == 1)
#elif defined(PATTERN_ALTERNATE_UPPER)
# define UPPER(letter, place) ((place) % 2 == 0)
#elif defined(PATTERN_THIRDS)
# define UPPER(letter, place) ((place) % 3 == 0)
#elif defined(PATTERN_HALVES)
# define UPPER(letter, place) ((letter) >= 'n')
#else
# error "choose a pattern: -DPATTERN_ALTERNATE_LOWER, -DPATTERN_ALTERNATE_UPPER, \
-DPATTERN_THIRDS or -DPATTERN_HALVES"
#endif

int	main(int ac, char **av)
{
	char	letter;
	char	shown;
	int		place;

	(void)ac;
	(void)av;
	letter = 'z';
	place = 0;
	while (letter >= 'a')
	{
		shown = letter;
		if (UPPER(letter, place))
			shown = letter - 'a' + 'A';
		write(1, &shown, 1);
		letter -= STEP;
		place++;
	}
	write(1, "\n", 1);
	return (0);
}
