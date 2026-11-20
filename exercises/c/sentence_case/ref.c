/*
** Reference solution of sentence_case (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSTYLE_CAMEL ref.c
*/

#include <unistd.h>

#if defined(STYLE_SNAKE) || defined(STYLE_CONSTANT)
# define SEPARATOR "_"
#elif defined(STYLE_KEBAB)
# define SEPARATOR "-"
#elif defined(STYLE_DOT)
# define SEPARATOR "."
#elif defined(STYLE_CAMEL) || defined(STYLE_PASCAL)
# define SEPARATOR ""
#else
# error "choose a style: -DSTYLE_CAMEL, -DSTYLE_PASCAL, -DSTYLE_SNAKE, -DSTYLE_KEBAB, \
-DSTYLE_CONSTANT or -DSTYLE_DOT"
#endif

static int	in_word(char c)
{
	return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'));
}

/* c written in the style: first tells it starts a word, words how many came before. */
static char	styled(char c, int first, int words)
{
	if (c >= 'A' && c <= 'Z')
		c = c - 'A' + 'a';
#if defined(STYLE_CONSTANT)
	(void)first;
	(void)words;
	if (c >= 'a' && c <= 'z')
		c = c - 'a' + 'A';
#elif defined(STYLE_PASCAL) || defined(STYLE_CAMEL)
# if defined(STYLE_CAMEL)
	if (first && words > 0 && c >= 'a' && c <= 'z')
# else
	(void)words;
	if (first && c >= 'a' && c <= 'z')
# endif
		c = c - 'a' + 'A';
#else
	(void)first;
	(void)words;
#endif
	return (c);
}

int	main(int ac, char **av)
{
	char	*separator;
	char	c;
	int		words;
	int		i;

	if (ac == 2)
	{
		words = 0;
		i = 0;
		while (av[1][i])
		{
			if (in_word(av[1][i]) && (i == 0 || !in_word(av[1][i - 1])))
			{
				separator = SEPARATOR;
				while (words > 0 && *separator)
					write(1, separator++, 1);
				c = styled(av[1][i], 1, words);
				words++;
			}
			else if (in_word(av[1][i]))
				c = styled(av[1][i], 0, words);
			else
			{
				i++;
				continue ;
			}
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
