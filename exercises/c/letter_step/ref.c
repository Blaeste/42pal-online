/*
** Reference solution of letter_step (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_CONSONANTS -DCASE_SWAP ref.c
*/

#include <unistd.h>

/* The group in order: a character moves to the next one, the last to the first. */
#if defined(WHAT_VOWELS)
# define GROUP "aeiou"
#elif defined(WHAT_CONSONANTS)
# define GROUP "bcdfghjklmnpqrstvwxyz"
#elif defined(WHAT_DIGITS)
# define GROUP "0123456789"
#elif defined(WHAT_BACKWARD_LETTERS)
# define GROUP "zyxwvutsrqponmlkjihgfedcba"
#else
# error "choose what moves: -DWHAT_VOWELS, -DWHAT_CONSONANTS, -DWHAT_DIGITS \
or -DWHAT_BACKWARD_LETTERS"
#endif

#if !defined(CASE_KEEP) && !defined(CASE_SWAP)
# error "choose the case: -DCASE_KEEP or -DCASE_SWAP"
#endif

static char	moved(char c)
{
	char	*group;
	int		upper;
	int		i;

	group = GROUP;
	upper = (c >= 'A' && c <= 'Z');
	if (upper)
		c = c - 'A' + 'a';
	i = 0;
	while (group[i] && group[i] != c)
		i++;
	if (!group[i])
		return (upper ? c - 'a' + 'A' : c);
	c = group[i + 1] ? group[i + 1] : group[0];
#if defined(CASE_SWAP)
	upper = !upper;
#endif
	if (upper && c >= 'a' && c <= 'z')
		c = c - 'a' + 'A';
	return (c);
}

int	main(int ac, char **av)
{
	char	c;
	int		i;

	if (ac == 2)
	{
		i = 0;
		while (av[1][i])
		{
			c = moved(av[1][i]);
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
