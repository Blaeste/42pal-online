/*
** Reference solution of char_line (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DCHAR_HASH -DCOUNT_10 ref.c
*/

#include <unistd.h>

#if defined(CHAR_HASH)
# define CHAR "#"
#elif defined(CHAR_DASH)
# define CHAR "-"
#elif defined(CHAR_EQUAL)
# define CHAR "="
#else
# error "choose a character: -DCHAR_HASH, -DCHAR_DASH or -DCHAR_EQUAL"
#endif

#if defined(COUNT_5)
# define COUNT 5
#elif defined(COUNT_10)
# define COUNT 10
#else
# error "choose a count: -DCOUNT_5 or -DCOUNT_10"
#endif

int	main(int ac, char **av)
{
	int	i;

	(void)ac;
	(void)av;
	i = 0;
	while (i++ < COUNT)
		write(1, CHAR, 1);
	write(1, "\n", 1);
	return (0);
}
