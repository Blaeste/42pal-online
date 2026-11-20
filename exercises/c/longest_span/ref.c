/*
** Reference solution of longest_span (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DRULE_REPEATED -DTIE_LAST ref.c
*/

#include <unistd.h>

#if !defined(RULE_UNIQUE) && !defined(RULE_REPEATED) && !defined(RULE_SORTED) \
	&& !defined(RULE_TWO_CHARS)
# error "choose a rule: -DRULE_UNIQUE, -DRULE_REPEATED, -DRULE_SORTED or -DRULE_TWO_CHARS"
#endif

#if !defined(TIE_FIRST) && !defined(TIE_LAST)
# error "choose a tie: -DTIE_FIRST or -DTIE_LAST"
#endif

static int	length_of(char *text)
{
	int	length;

	length = 0;
	while (text[length])
		length++;
	return (length);
}

#if defined(RULE_REPEATED)

/* True if the part at a and the part at b, length long, are the same. */
static int	same(char *a, char *b, int length)
{
	int	i;

	i = 0;
	while (i < length && a[i] == b[i])
		i++;
	return (i == length);
}

#endif

/* True if the part of text at start, length long, follows the rule. */
static int	follows(char *text, int size, int start, int length)
{
	int	i;
#if defined(RULE_UNIQUE) || defined(RULE_TWO_CHARS)
	int	seen[256];
	int	kinds;

	i = 0;
	while (i < 256)
		seen[i++] = 0;
	kinds = 0;
	i = start;
	while (i < start + length)
	{
		if (seen[(unsigned char)text[i]]++ == 0)
			kinds++;
		i++;
	}
	(void)size;
# if defined(RULE_UNIQUE)
	return (kinds == length);
# else
	return (kinds <= 2);
# endif
#elif defined(RULE_SORTED)
	(void)size;
	i = start + 1;
	while (i < start + length)
	{
		if (text[i - 1] > text[i])
			return (0);
		i++;
	}
	return (1);
#else
	i = 0;
	while (i + length <= size)
	{
		if (i != start && same(text + i, text + start, length))
			return (1);
		i++;
	}
	return (0);
#endif
}

/* Displays the longest part that follows the rule: the first or the last one. */
static void	put_longest(char *text)
{
	int	size;
	int	length;
	int	start;

	size = length_of(text);
	length = size;
	while (length > 0)
	{
#if defined(TIE_FIRST)
		start = 0;
		while (start + length <= size)
		{
			if (follows(text, size, start, length))
			{
				write(1, text + start, length);
				return ;
			}
			start++;
		}
#else
		start = size - length;
		while (start >= 0)
		{
			if (follows(text, size, start, length))
			{
				write(1, text + start, length);
				return ;
			}
			start--;
		}
#endif
		length--;
	}
}

int	main(int ac, char **av)
{
	if (ac == 2)
		put_longest(av[1]);
	write(1, "\n", 1);
	return (0);
}
