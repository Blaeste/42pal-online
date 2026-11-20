/*
** Reference solution of word_rotate (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DMOVE_LONGEST_FIRST ref.c
*/

#include <unistd.h>

#if !defined(MOVE_SWAP_ENDS) && !defined(MOVE_FIRST_TWO_LAST) && !defined(MOVE_LONGEST_FIRST) \
	&& !defined(MOVE_SHORTEST_LAST)
# error "choose a move: -DMOVE_SWAP_ENDS, -DMOVE_FIRST_TWO_LAST, -DMOVE_LONGEST_FIRST \
or -DMOVE_SHORTEST_LAST"
#endif

/* A string has at most this many words. */
#define MAX_WORDS 1024

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

int	main(int ac, char **av)
{
	char	*starts[MAX_WORDS];
	int		lengths[MAX_WORDS];
	int		order[MAX_WORDS];
	int		count;
	int		chosen;
	int		i;
	int		j;

	count = 0;
	i = 0;
	while (ac == 2 && av[1][i] && count < MAX_WORDS)
	{
		while (is_blank(av[1][i]))
			i++;
		if (!av[1][i])
			break ;
		starts[count] = av[1] + i;
		lengths[count] = 0;
		while (av[1][i] && !is_blank(av[1][i]))
		{
			lengths[count]++;
			i++;
		}
		count++;
	}
	/* order: the words, by their index, in the order they are displayed. */
	j = 0;
	chosen = 0;
	i = 0;
	while (i < count)
	{
#if defined(MOVE_LONGEST_FIRST)
		if (lengths[i] > lengths[chosen])
			chosen = i;
#elif defined(MOVE_SHORTEST_LAST)
		if (lengths[i] < lengths[chosen])
			chosen = i;
#endif
		i++;
	}
#if defined(MOVE_SWAP_ENDS) || defined(MOVE_FIRST_TWO_LAST)
	(void)chosen;
#endif
	i = -1;
	while (++i < count)
	{
#if defined(MOVE_SWAP_ENDS)
		order[j++] = (i == 0) ? count - 1 : (i == count - 1) ? 0 : i;
#elif defined(MOVE_FIRST_TWO_LAST)
		/* From the third word on, then the first two; two words or fewer stay. */
		order[j++] = (count > 2) ? (i + 2) % count : i;
#elif defined(MOVE_LONGEST_FIRST)
		if (i == 0)
			order[j++] = chosen;
		if (i != chosen)
			order[j++] = i;
#else
		if (i != chosen)
			order[j++] = i;
		if (i == count - 1)
			order[j++] = chosen;
#endif
	}
	i = -1;
	while (++i < count)
	{
		if (i > 0)
			write(1, " ", 1);
		write(1, starts[order[i]], lengths[order[i]]);
	}
	write(1, "\n", 1);
	return (0);
}
