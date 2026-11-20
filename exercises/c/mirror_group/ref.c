/*
** Reference solution of mirror_group (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DGROUP_HALVES -DCASE_SWAP ref.c
*/

#include <unistd.h>

/* The parts of the group, each turned around on its own. */
#if defined(GROUP_VOWELS)
# define PART_1 "aeiou"
# define PART_2 ""
#elif defined(GROUP_CONSONANTS)
# define PART_1 "bcdfghjklmnpqrstvwxyz"
# define PART_2 ""
#elif defined(GROUP_DIGITS)
# define PART_1 "0123456789"
# define PART_2 ""
#elif defined(GROUP_HALVES)
# define PART_1 "abcdefghijklm"
# define PART_2 "nopqrstuvwxyz"
#else
# error "choose a group: -DGROUP_VOWELS, -DGROUP_CONSONANTS, -DGROUP_DIGITS or -DGROUP_HALVES"
#endif

#if !defined(CASE_KEEP) && !defined(CASE_SWAP)
# error "choose the case: -DCASE_KEEP or -DCASE_SWAP"
#endif

/* c turned around in `part`, or 0 if it is not in it. */
static char	in_part(char c, char *part)
{
	int	length;
	int	i;

	length = 0;
	while (part[length])
		length++;
	i = 0;
	while (i < length)
	{
		if (part[i] == c)
			return (part[length - 1 - i]);
		i++;
	}
	return (0);
}

static char	mirrored(char c)
{
	int		upper;
	char	after;

	upper = (c >= 'A' && c <= 'Z');
	if (upper)
		c = c - 'A' + 'a';
	after = in_part(c, PART_1);
	if (!after)
		after = in_part(c, PART_2);
	if (!after)
		return (upper ? c - 'a' + 'A' : c);
#if defined(CASE_SWAP)
	upper = !upper;
#endif
	if (upper && after >= 'a' && after <= 'z')
		after = after - 'a' + 'A';
	return (after);
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
			c = mirrored(av[1][i]);
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
