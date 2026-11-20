/*
** Reference solution of word_from_end (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LAST_DIGIT -DHOW_UPPER ref.c
*/

#include <unistd.h>

#if !defined(WHICH_SECOND_LAST) && !defined(WHICH_LAST_TWO) && !defined(WHICH_LAST_CAPITAL) \
	&& !defined(WHICH_LAST_DIGIT)
# error "choose which: -DWHICH_SECOND_LAST, -DWHICH_LAST_TWO, -DWHICH_LAST_CAPITAL \
or -DWHICH_LAST_DIGIT"
#endif

#if !defined(HOW_PLAIN) && !defined(HOW_UPPER)
# error "choose how: -DHOW_PLAIN or -DHOW_UPPER"
#endif

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

static void	put_part(char *text, int start, int end)
{
	char	c;

	while (start < end)
	{
		c = text[start++];
#if defined(HOW_UPPER)
		if (c >= 'a' && c <= 'z')
			c = c - 'a' + 'A';
#endif
		write(1, &c, 1);
	}
}

#if defined(WHICH_LAST_CAPITAL) || defined(WHICH_LAST_DIGIT)

/* True if the word from start to end is the kind looked for. */
static int	wanted(char *text, int start, int end)
{
# if defined(WHICH_LAST_CAPITAL)
	(void)end;
	return (text[start] >= 'A' && text[start] <= 'Z');
# else
	while (start < end)
	{
		if (text[start] >= '0' && text[start] <= '9')
			return (1);
		start++;
	}
	return (0);
# endif
}

#endif

int	main(int ac, char **av)
{
	char	*text;
	int		i;
	int		start;
	int		starts[2];
	int		ends[2];
	int		count;

	if (ac == 2)
	{
		text = av[1];
		starts[0] = 0;
		starts[1] = 0;
		ends[0] = 0;
		ends[1] = 0;
		count = 0;
		i = 0;
		while (text[i])
		{
			while (is_blank(text[i]))
				i++;
			if (!text[i])
				break ;
			start = i;
			while (text[i] && !is_blank(text[i]))
				i++;
#if defined(WHICH_LAST_CAPITAL) || defined(WHICH_LAST_DIGIT)
			if (!wanted(text, start, i))
				continue ;
#endif
			/* Keep the last two words found: [0] the one before, [1] the last. */
			starts[0] = starts[1];
			ends[0] = ends[1];
			starts[1] = start;
			ends[1] = i;
			count++;
		}
#if defined(WHICH_SECOND_LAST)
		if (count >= 2)
			put_part(text, starts[0], ends[0]);
#elif defined(WHICH_LAST_TWO)
		if (count >= 2)
		{
			put_part(text, starts[0], ends[0]);
			write(1, " ", 1);
			put_part(text, starts[1], ends[1]);
		}
#else
		if (count >= 1)
			put_part(text, starts[1], ends[1]);
#endif
	}
	write(1, "\n", 1);
	return (0);
}
