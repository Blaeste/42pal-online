/*
** Reference solution of merge_chars (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_ONCE -DORDER_ASCII ref.c
*/

#include <unistd.h>

#if !defined(WHICH_ALL) && !defined(WHICH_ONCE) && !defined(WHICH_LETTERS)
# error "choose which: -DWHICH_ALL, -DWHICH_ONCE or -DWHICH_LETTERS"
#endif

#if !defined(ORDER_APPEARANCE) && !defined(ORDER_ASCII) && !defined(ORDER_REVERSE_ASCII)
# error "choose an order: -DORDER_APPEARANCE, -DORDER_ASCII or -DORDER_REVERSE_ASCII"
#endif

/* in_first[c], in_second[c]: c is in the first, the second string. */
static int	in_first[256];
static int	in_second[256];

/* True if c is to be displayed. */
static int	kept(unsigned char c)
{
#if defined(WHICH_ONCE)
	return (in_first[c] != in_second[c]);
#elif defined(WHICH_LETTERS)
	return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'));
#else
	(void)c;
	return (1);
#endif
}

int	main(int ac, char **av)
{
	int				shown[256];
	unsigned char	c;
	int				i;
	int				s;

	if (ac == 3)
	{
		i = -1;
		while (++i < 256)
			shown[i] = 0;
		i = -1;
		while (av[1][++i])
			in_first[(unsigned char)av[1][i]] = 1;
		i = -1;
		while (av[2][++i])
			in_second[(unsigned char)av[2][i]] = 1;
#if defined(ORDER_APPEARANCE)
		s = 0;
		while (++s <= 2)
		{
			i = -1;
			while (av[s][++i])
			{
				c = av[s][i];
				if (!shown[c] && kept(c))
				{
					shown[c] = 1;
					write(1, &c, 1);
				}
			}
		}
#else
		(void)s;
		i = 0;
		while (i < 256)
		{
# if defined(ORDER_ASCII)
			c = i;
# else
			c = 255 - i;
# endif
			if ((in_first[c] || in_second[c]) && kept(c))
				write(1, &c, 1);
			i++;
		}
		(void)shown;
#endif
	}
	write(1, "\n", 1);
	return (0);
}
