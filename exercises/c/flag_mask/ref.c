/*
** Reference solution of flag_mask (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSHOW_HEX -DREPEAT_TOGGLE ref.c
*/

#include <unistd.h>

#if !defined(SHOW_LETTERS) && !defined(SHOW_MASK) && !defined(SHOW_HEX)
# error "choose a show: -DSHOW_LETTERS, -DSHOW_MASK or -DSHOW_HEX"
#endif

#if !defined(REPEAT_SET) && !defined(REPEAT_TOGGLE)
# error "choose a repeat: -DREPEAT_SET or -DREPEAT_TOGGLE"
#endif

#if defined(SHOW_HEX)

static void	put_hex(unsigned int n)
{
	if (n >= 16)
		put_hex(n / 16);
	write(1, &"0123456789abcdef"[n % 16], 1);
}

static void	show(unsigned int mask)
{
	put_hex(mask);
	write(1, "\n", 1);
}

#else

static void	show(unsigned int mask)
{
	char	c;
	int		bit;

	bit = 0;
	while (bit < 26)
	{
# if defined(SHOW_LETTERS)
		c = 'a' + bit;
		if (mask >> bit & 1)
			write(1, &c, 1);
# else
		c = '0' + (mask >> bit & 1);
		write(1, &c, 1);
# endif
		bit++;
	}
	write(1, "\n", 1);
}

#endif

int	main(int ac, char **av)
{
	unsigned int	mask;
	int				i;
	int				j;

	if (ac < 2)
		return (write(1, "\n", 1), 0);
	mask = 0;
	i = 0;
	while (++i < ac)
	{
		if (av[i][0] != '-')
			continue ;
		j = 0;
		while (av[i][++j])
		{
			if (av[i][j] < 'a' || av[i][j] > 'z')
				return (write(1, "Bad option\n", 11), 0);
#if defined(REPEAT_SET)
			mask |= 1u << (av[i][j] - 'a');
#else
			mask ^= 1u << (av[i][j] - 'a');
#endif
		}
	}
	show(mask);
	return (0);
}
