/*
** Reference solution of param_from_end (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LAST_TWO -DHOW_REVERSED ref.c
*/

#include <unistd.h>

#if !defined(WHICH_SECOND_LAST) && !defined(WHICH_LAST_TWO)
# error "choose which: -DWHICH_SECOND_LAST or -DWHICH_LAST_TWO"
#endif

#if !defined(HOW_PLAIN) && !defined(HOW_UPPER) && !defined(HOW_REVERSED)
# error "choose how: -DHOW_PLAIN, -DHOW_UPPER or -DHOW_REVERSED"
#endif

static void	put_arg(char *arg)
{
	char	c;
	int		length;
	int		i;

	length = 0;
	while (arg[length])
		length++;
	i = 0;
	while (i < length)
	{
#if defined(HOW_REVERSED)
		c = arg[length - 1 - i];
#else
		c = arg[i];
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
	if (ac >= 3)
	{
		put_arg(av[ac - 2]);
#if defined(WHICH_LAST_TWO)
		write(1, " ", 1);
		put_arg(av[ac - 1]);
#endif
	}
	write(1, "\n", 1);
	return (0);
}
