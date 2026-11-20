/*
** Reference solution of put_filter (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_DOUBLED -DEND_NEWLINE ref.c main_42pal.c
*/

#include <unistd.h>

#if defined(WHAT_LETTERS)
# define WHAT_NAME letters
#elif defined(WHAT_DIGITS)
# define WHAT_NAME digits
#elif defined(WHAT_UPPER)
# define WHAT_NAME upper
#elif defined(WHAT_DOUBLED)
# define WHAT_NAME doubled
#else
# error "choose what to display: -DWHAT_LETTERS, -DWHAT_DIGITS, -DWHAT_UPPER or -DWHAT_DOUBLED"
#endif

#if defined(END_BARE)
# define END_NAME _bare
#elif defined(END_NEWLINE)
# define END_NAME _newline
#else
# error "choose the end: -DEND_BARE or -DEND_NEWLINE"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_put_, WHAT_NAME, END_NAME)

void	FT_NAME(char *str)
{
	char	c;

	while (*str)
	{
		c = *str++;
#if defined(WHAT_LETTERS)
		if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'))
			write(1, &c, 1);
#elif defined(WHAT_DIGITS)
		if (c >= '0' && c <= '9')
			write(1, &c, 1);
#elif defined(WHAT_UPPER)
		if (c >= 'a' && c <= 'z')
			c = c - 'a' + 'A';
		write(1, &c, 1);
#else
		write(1, &c, 1);
		write(1, &c, 1);
#endif
	}
#if defined(END_NEWLINE)
	write(1, "\n", 1);
#endif
}
