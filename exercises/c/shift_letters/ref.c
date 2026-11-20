/*
** Reference solution of shift_letters, for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSHIFT_3 -DDIRECTION_BACKWARD -DLETTERS_ALL ref.c
*/

#include <unistd.h>

#if defined(SHIFT_2)
# define SHIFT 2
#elif defined(SHIFT_3)
# define SHIFT 3
#elif defined(SHIFT_5)
# define SHIFT 5
#else
# error "choose a shift: -DSHIFT_2, -DSHIFT_3 or -DSHIFT_5"
#endif

/* Moving back by SHIFT is moving forward by 26 - SHIFT. */
#if defined(DIRECTION_FORWARD)
# define STEP SHIFT
#elif defined(DIRECTION_BACKWARD)
# define STEP (26 - SHIFT)
#else
# error "choose a direction: -DDIRECTION_FORWARD or -DDIRECTION_BACKWARD"
#endif

#if !defined(LETTERS_ALL) && !defined(LETTERS_LOWERCASE) && !defined(LETTERS_UPPERCASE)
# error "choose letters: -DLETTERS_ALL, -DLETTERS_LOWERCASE or -DLETTERS_UPPERCASE"
#endif

static char	shift(char c)
{
#if !defined(LETTERS_UPPERCASE)
	if (c >= 'a' && c <= 'z')
		return ((c - 'a' + STEP) % 26 + 'a');
#endif
#if !defined(LETTERS_LOWERCASE)
	if (c >= 'A' && c <= 'Z')
		return ((c - 'A' + STEP) % 26 + 'A');
#endif
	return (c);
}

int	main(int ac, char **av)
{
	int		i;
	char	c;

	if (ac == 2)
	{
		i = 0;
		while (av[1][i])
		{
			c = shift(av[1][i]);
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
