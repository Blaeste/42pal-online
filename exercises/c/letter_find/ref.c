/*
** Reference solution of letter_find (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DLETTER_E -DCASE_ANY_CASE ref.c
*/

#include <unistd.h>

#if defined(LETTER_E)
# define LETTER 'e'
#elif defined(LETTER_O)
# define LETTER 'o'
#elif defined(LETTER_S)
# define LETTER 's'
#else
# error "choose a letter: -DLETTER_E, -DLETTER_O or -DLETTER_S"
#endif

#if !defined(CASE_EXACT) && !defined(CASE_ANY_CASE)
# error "choose the case: -DCASE_EXACT or -DCASE_ANY_CASE"
#endif

int	main(int ac, char **av)
{
	char	letter;
	int		i;

	letter = LETTER;
	if (ac != 2)
	{
		write(1, &letter, 1);
		write(1, "\n", 1);
		return (0);
	}
	i = 0;
	while (av[1][i])
	{
#if defined(CASE_ANY_CASE)
		if (av[1][i] == LETTER || av[1][i] == LETTER - 'a' + 'A')
#else
		if (av[1][i] == LETTER)
#endif
		{
			write(1, &av[1][i], 1);
			break ;
		}
		i++;
	}
	write(1, "\n", 1);
	return (0);
}
