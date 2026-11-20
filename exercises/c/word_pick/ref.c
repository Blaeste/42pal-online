/*
** Reference solution of word_pick (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LONGEST -DHOW_UPPER ref.c
*/

#include <unistd.h>

#if !defined(WHICH_FIRST) && !defined(WHICH_SECOND) && !defined(WHICH_LAST) \
	&& !defined(WHICH_LONGEST)
# error "choose a word: -DWHICH_FIRST, -DWHICH_SECOND, -DWHICH_LAST or -DWHICH_LONGEST"
#endif

#if !defined(HOW_PLAIN) && !defined(HOW_UPPER) && !defined(HOW_REVERSED)
# error "choose how: -DHOW_PLAIN, -DHOW_UPPER or -DHOW_REVERSED"
#endif

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

/*
** Finds the word to display: *start points to it, and its length is
** returned; 0 when there is no such word.
*/
static int	find_word(char *text, char **start)
{
	int	i;
	int	length;
	int	count;
	int	found;

	i = 0;
	count = 0;
	found = 0;
	while (text[i])
	{
		while (is_blank(text[i]))
			i++;
		if (!text[i])
			break ;
		length = 0;
		while (text[i + length] && !is_blank(text[i + length]))
			length++;
		count++;
#if defined(WHICH_FIRST)
		if (count == 1)
#elif defined(WHICH_SECOND)
		if (count == 2)
#elif defined(WHICH_LONGEST)
		if (length > found)
#else
		if (1)
#endif
		{
			*start = text + i;
			found = length;
		}
		i += length;
	}
	return (found);
}

static void	put_word(char *word, int length)
{
	int		i;
	char	c;

	i = 0;
	while (i < length)
	{
#if defined(HOW_REVERSED)
		c = word[length - 1 - i];
#else
		c = word[i];
#endif
#if defined(HOW_UPPER)
		if (c >= 'a' && c <= 'z')
			c = c - 'a' + 'A';
#endif
		write(1, &c, 1);
		i++;
	}
}

int	main(int ac, char **av)
{
	char	*word;
	int		length;

	if (ac == 2)
	{
		length = find_word(av[1], &word);
		if (length > 0)
			put_word(word, length);
	}
	write(1, "\n", 1);
	return (0);
}
