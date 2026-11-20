/*
** Reference solution of word_each (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_SHORTEST -DJOIN_SPACES ref.c
*/

#include <unistd.h>

#if !defined(WHICH_SHORTEST) && !defined(WHICH_LONGEST) && !defined(WHICH_SECOND)
# error "choose which: -DWHICH_SHORTEST, -DWHICH_LONGEST or -DWHICH_SECOND"
#endif

#if !defined(JOIN_LINES) && !defined(JOIN_SPACES)
# error "choose join: -DJOIN_LINES or -DJOIN_SPACES"
#endif

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

/* The word of text the variant wants: its start in *start, its length returned (0: none). */
static int	pick(char *text, char **start)
{
	int	i;
	int	length;
	int	best;
	int	rank;

	best = 0;
	rank = 0;
	i = 0;
	while (text[i])
	{
		while (is_blank(text[i]))
			i++;
		length = 0;
		while (text[i + length] && !is_blank(text[i + length]))
			length++;
		if (length == 0)
			break ;
		rank++;
#if defined(WHICH_SECOND)
		if (rank == 2)
#elif defined(WHICH_SHORTEST)
		if (best == 0 || length < best)
#else
		if (length > best)
#endif
		{
			best = length;
			*start = text + i;
		}
		i += length;
	}
	return (best);
}

int	main(int ac, char **av)
{
	char	*start;
	int		length;
	int		shown;
	int		i;

	shown = 0;
	i = 0;
	while (++i < ac)
	{
		length = pick(av[i], &start);
#if defined(JOIN_LINES)
		write(1, start, length);
		write(1, "\n", 1);
		(void)shown;
#else
		if (length == 0)
			continue ;
		if (shown++)
			write(1, " ", 1);
		write(1, start, length);
#endif
	}
#if defined(JOIN_SPACES)
	write(1, "\n", 1);
#else
	if (ac == 1)
		write(1, "\n", 1);
#endif
	return (0);
}
