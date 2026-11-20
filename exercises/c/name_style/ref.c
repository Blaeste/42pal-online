/*
** Reference solution of name_style (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSOURCE_KEBAB -DTARGET_PASCAL ref.c
*/

#include <unistd.h>

/* In the source name, words are cut by a separator, or by uppercase letters. */
#if defined(SOURCE_SNAKE) || defined(SOURCE_CONSTANT)
# define SEPARATOR_IN '_'
#elif defined(SOURCE_KEBAB)
# define SEPARATOR_IN '-'
#elif !defined(SOURCE_CAMEL) && !defined(SOURCE_PASCAL)
# error "choose a source style: -DSOURCE_SNAKE, -DSOURCE_KEBAB, \
-DSOURCE_CAMEL, -DSOURCE_PASCAL or -DSOURCE_CONSTANT"
#endif

#if !defined(TARGET_SNAKE) && !defined(TARGET_KEBAB) && !defined(TARGET_CAMEL) \
	&& !defined(TARGET_PASCAL) && !defined(TARGET_CONSTANT)
# error "choose a target style: -DTARGET_SNAKE, -DTARGET_KEBAB, \
-DTARGET_CAMEL, -DTARGET_PASCAL or -DTARGET_CONSTANT"
#endif

static void	put_char(char c)
{
	write(1, &c, 1);
}

/* Each one only where the target style uses it: -Werror refuses the others. */
#if !defined(TARGET_CONSTANT)

static char	to_lower(char c)
{
	if (c >= 'A' && c <= 'Z')
		return (c - 'A' + 'a');
	return (c);
}

#endif
#if !defined(TARGET_SNAKE) && !defined(TARGET_KEBAB)

static char	to_upper(char c)
{
	if (c >= 'a' && c <= 'z')
		return (c - 'a' + 'A');
	return (c);
}

#endif

/* True if the letter at name[i] is the first one of a word. */
static int	starts_word(char *name, int i)
{
#if defined(SEPARATOR_IN)
	return (i == 0 || name[i - 1] == SEPARATOR_IN);
#else
	return (i == 0 || (name[i] >= 'A' && name[i] <= 'Z'));
#endif
}

/*
** Writes the letter c in the target style: first tells that it starts a
** word, i that it is the first letter of the name.
*/
static void	put_letter(char c, int first, int i)
{
#if defined(TARGET_SNAKE) || defined(TARGET_CONSTANT)
	if (first && i > 0)
		put_char('_');
#elif defined(TARGET_KEBAB)
	if (first && i > 0)
		put_char('-');
#endif
#if defined(TARGET_CONSTANT)
	(void)first;
	put_char(to_upper(c));
#elif defined(TARGET_PASCAL)
	(void)i;
	if (first)
		put_char(to_upper(c));
	else
		put_char(to_lower(c));
#elif defined(TARGET_CAMEL)
	if (first && i > 0)
		put_char(to_upper(c));
	else
		put_char(to_lower(c));
#else
	put_char(to_lower(c));
#endif
}

int	main(int ac, char **av)
{
	int	i;

	if (ac == 2)
	{
		i = 0;
		while (av[1][i])
		{
#if defined(SEPARATOR_IN)
			if (av[1][i] != SEPARATOR_IN)
				put_letter(av[1][i], starts_word(av[1], i), i);
#else
			put_letter(av[1][i], starts_word(av[1], i), i);
#endif
			i++;
		}
	}
	put_char('\n');
	return (0);
}
