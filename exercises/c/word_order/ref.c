/*
** Reference solution of word_order, for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DORDER_SORT -DSEPARATOR_COMMA ref.c
*/

#include <unistd.h>

#if !defined(ORDER_REVERSE) && !defined(ORDER_ROTATE_LEFT) && !defined(ORDER_ROTATE_RIGHT) \
	&& !defined(ORDER_SORT) && !defined(ORDER_BY_LENGTH)
# error "choose an order: -DORDER_REVERSE, _ROTATE_LEFT, _ROTATE_RIGHT, _SORT or _BY_LENGTH"
#endif

#if defined(SEPARATOR_SPACE)
# define SEPARATOR " "
#elif defined(SEPARATOR_NEWLINE)
# define SEPARATOR "\n"
#elif defined(SEPARATOR_COMMA)
# define SEPARATOR ", "
#else
# error "choose a separator: -DSEPARATOR_SPACE, _NEWLINE or _COMMA"
#endif

/* No malloc allowed: the words of the string fit in these arrays. */
#define MAX_WORDS 4096

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

/* Note where each word starts and how long it is; return how many. */
static int	cut_words(char *s, char **words, int *lengths)
{
	int	count;

	count = 0;
	while (*s && count < MAX_WORDS)
	{
		while (*s && is_blank(*s))
			s++;
		if (!*s)
			break ;
		words[count] = s;
		lengths[count] = 0;
		while (s[lengths[count]] && !is_blank(s[lengths[count]]))
			lengths[count]++;
		s += lengths[count];
		count++;
	}
	return (count);
}

#if defined(ORDER_SORT) || defined(ORDER_BY_LENGTH)

/* True when word a must come before word b. */
static int	before(char **words, int *lengths, int a, int b)
{
# if defined(ORDER_SORT)
	int	i;

	i = 0;
	while (i < lengths[a] && i < lengths[b] && words[a][i] == words[b][i])
		i++;
	if (i < lengths[a] && i < lengths[b])
		return ((unsigned char)words[a][i] < (unsigned char)words[b][i]);
	return (lengths[a] < lengths[b]);
# else
	(void)words;
	return (lengths[a] < lengths[b]);
# endif
}

/* An insertion sort of the word numbers: stable, as long words keep their order. */
static void	sort(char **words, int *lengths, int *order, int count)
{
	int	i;
	int	j;
	int	key;

	i = 1;
	while (i < count)
	{
		key = order[i];
		j = i - 1;
		while (j >= 0 && before(words, lengths, key, order[j]))
		{
			order[j + 1] = order[j];
			j--;
		}
		order[j + 1] = key;
		i++;
	}
}

#endif

/* The word numbers, in the order of the variant. */
static void	put_in_order(char **words, int *lengths, int *order, int count)
{
	int	i;

	i = -1;
	while (++i < count)
	{
#if defined(ORDER_REVERSE)
		order[i] = count - 1 - i;
#elif defined(ORDER_ROTATE_LEFT)
		order[i] = (i + 1) % count;
#elif defined(ORDER_ROTATE_RIGHT)
		order[i] = (i + count - 1) % count;
#else
		order[i] = i;
#endif
	}
#if defined(ORDER_SORT) || defined(ORDER_BY_LENGTH)
	sort(words, lengths, order, count);
#else
	(void)words;
	(void)lengths;
#endif
}

int	main(int ac, char **av)
{
	char	*words[MAX_WORDS];
	int		lengths[MAX_WORDS];
	int		order[MAX_WORDS];
	int		count;
	int		i;

	if (ac == 2)
	{
		count = cut_words(av[1], words, lengths);
		put_in_order(words, lengths, order, count);
		i = 0;
		while (i < count)
		{
			if (i > 0)
				write(1, SEPARATOR, sizeof(SEPARATOR) - 1);
			write(1, words[order[i]], lengths[order[i]]);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
