/*
** Reference solution of word_spread (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DGAP_TAB -DENDS_AROUND ref.c
*/

#include <unistd.h>

#if defined(GAP_2)
# define GAP "  "
#elif defined(GAP_4)
# define GAP "    "
#elif defined(GAP_TAB)
# define GAP "\t"
#else
# error "choose a gap: -DGAP_2, -DGAP_4 or -DGAP_TAB"
#endif

#if !defined(ENDS_INSIDE) && !defined(ENDS_AROUND)
# error "choose the ends: -DENDS_INSIDE or -DENDS_AROUND"
#endif

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

static void	put_gap(void)
{
	char	*gap;

	gap = GAP;
	while (*gap)
		write(1, gap++, 1);
}

int	main(int ac, char **av)
{
	int	words;
	int	i;

	if (ac == 2)
	{
		words = 0;
		i = 0;
		while (av[1][i])
		{
			while (is_blank(av[1][i]))
				i++;
			if (!av[1][i])
				break ;
#if defined(ENDS_AROUND)
			put_gap();
#else
			if (words > 0)
				put_gap();
#endif
			while (av[1][i] && !is_blank(av[1][i]))
				write(1, &av[1][i++], 1);
			words++;
		}
#if defined(ENDS_AROUND)
		if (words > 0)
			put_gap();
#endif
	}
	write(1, "\n", 1);
	return (0);
}
