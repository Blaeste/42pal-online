/*
** Reference solution of char_only (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DCHAR_K -DEND_NEWLINE ref.c
*/

#include <unistd.h>

#if defined(CHAR_E)
# define CHAR "e"
#elif defined(CHAR_K)
# define CHAR "k"
#elif defined(CHAR_X)
# define CHAR "x"
#elif defined(CHAR_7)
# define CHAR "7"
#else
# error "choose a character: -DCHAR_E, -DCHAR_K, -DCHAR_X or -DCHAR_7"
#endif

#if !defined(END_BARE) && !defined(END_NEWLINE)
# error "choose the end: -DEND_BARE or -DEND_NEWLINE"
#endif

int	main(int ac, char **av)
{
	(void)ac;
	(void)av;
	write(1, CHAR, 1);
#if defined(END_NEWLINE)
	write(1, "\n", 1);
#endif
	return (0);
}
