/*
** Reference solution of char_filter, for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DMODE_COMMON -DORDER_ASCII -DSEPARATOR_SPACE ref.c
*/

#include <unistd.h>

#if !defined(MODE_COMMON) && !defined(MODE_ONLY_FIRST) && !defined(MODE_ONLY_SECOND)
# error "choose a mode: -DMODE_COMMON, -DMODE_ONLY_FIRST or -DMODE_ONLY_SECOND"
#endif
#if !defined(ORDER_APPEARANCE) && !defined(ORDER_ASCII)
# error "choose an order: -DORDER_APPEARANCE or -DORDER_ASCII"
#endif
#if !defined(SEPARATOR_NONE) && !defined(SEPARATOR_SPACE)
# error "choose a separator: -DSEPARATOR_NONE or -DSEPARATOR_SPACE"
#endif

static int	is_in(char *s, char c)
{
	while (*s)
	{
		if (*s == c)
			return (1);
		s++;
	}
	return (0);
}

/* True when c is in the set of characters the mode asks for. */
static int	belongs(char c, char *s1, char *s2)
{
#if defined(MODE_COMMON)
	return (is_in(s1, c) && is_in(s2, c));
#elif defined(MODE_ONLY_FIRST)
	return (is_in(s1, c) && !is_in(s2, c));
#else
	return (is_in(s2, c) && !is_in(s1, c));
#endif
}

/* Print c, after a space unless it is the first character printed. */
static void	put(char c, int *first)
{
#if defined(SEPARATOR_SPACE)
	if (!*first)
		write(1, " ", 1);
#endif
	*first = 0;
	write(1, &c, 1);
}

#if defined(ORDER_APPEARANCE)

/* Print, in order, the characters of s that belong and were not seen yet. */
static void	walk(char *s, char **av, int *seen, int *first)
{
	while (*s)
	{
		if (!seen[(unsigned char)*s] && belongs(*s, av[1], av[2]))
		{
			seen[(unsigned char)*s] = 1;
			put(*s, first);
		}
		s++;
	}
}

static void	print_set(char **av)
{
	int	seen[256];
	int	first;
	int	i;

	i = 0;
	while (i < 256)
		seen[i++] = 0;
	first = 1;
	walk(av[1], av, seen, &first);
	walk(av[2], av, seen, &first);
}

#else

/* Every character, by increasing ASCII value: each one printed once. */
static void	print_set(char **av)
{
	int	first;
	int	c;

	first = 1;
	c = 1;
	while (c < 256)
	{
		if (belongs((char)c, av[1], av[2]))
			put((char)c, &first);
		c++;
	}
}

#endif

int	main(int ac, char **av)
{
	if (ac == 3)
		print_set(av);
	write(1, "\n", 1);
	return (0);
}
