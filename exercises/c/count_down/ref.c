/*
** Reference solution of count_down (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSTART_12 -DSEPARATOR_COMMA ref.c
*/

#include <unistd.h>

#if defined(START_5)
# define START 5
#elif defined(START_7)
# define START 7
#elif defined(START_12)
# define START 12
#else
# error "choose a start: -DSTART_5, -DSTART_7 or -DSTART_12"
#endif

#if defined(SEPARATOR_SPACE)
# define SEPARATOR " "
#elif defined(SEPARATOR_COMMA)
# define SEPARATOR ", "
#else
# error "choose a separator: -DSEPARATOR_SPACE or -DSEPARATOR_COMMA"
#endif

int	main(int ac, char **av)
{
	char	digit;
	char	*separator;
	int		n;

	(void)ac;
	(void)av;
	n = START;
	while (n >= 0)
	{
		if (n >= 10)
		{
			digit = '0' + n / 10;
			write(1, &digit, 1);
		}
		digit = '0' + n % 10;
		write(1, &digit, 1);
		separator = SEPARATOR;
		while (n > 0 && *separator)
			write(1, separator++, 1);
		n--;
	}
	write(1, "\n", 1);
	return (0);
}
