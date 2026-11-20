/*
** Reference solution of alpha_wave (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWAVE_2 -DSTART_LOWER -DSEPARATOR_JOINED ref.c
*/

#include <unistd.h>

#if defined(WAVE_1)
# define WAVE 1
#elif defined(WAVE_2)
# define WAVE 2
#elif defined(WAVE_3)
# define WAVE 3
#else
# error "choose a wave: -DWAVE_1, -DWAVE_2 or -DWAVE_3"
#endif

/* The parity of the waves in uppercase: 0 for the first wave, 1 for the second. */
#if defined(START_UPPER)
# define UPPER_WAVES 0
#elif defined(START_LOWER)
# define UPPER_WAVES 1
#else
# error "choose a start: -DSTART_LOWER or -DSTART_UPPER"
#endif

#if !defined(SEPARATOR_JOINED) && !defined(SEPARATOR_SPACED)
# error "choose a separator: -DSEPARATOR_JOINED or -DSEPARATOR_SPACED"
#endif

int	main(int ac, char **av)
{
	int		i;
	char	letter;

	(void)ac;
	(void)av;
	i = 0;
	while (i < 26)
	{
		letter = 'a' + i;
		if ((i / WAVE) % 2 == UPPER_WAVES)
			letter = letter - 'a' + 'A';
#if defined(SEPARATOR_SPACED)
		if (i > 0)
			write(1, " ", 1);
#endif
		write(1, &letter, 1);
		i++;
	}
	write(1, "\n", 1);
	return (0);
}
