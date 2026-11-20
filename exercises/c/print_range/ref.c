/*
** Reference solution of print_range (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DCHARS_DIGITS -DORDER_UP -DSTEP_SKIP ref.c main_42pal.c
*/

#include <unistd.h>

#if defined(CHARS_DIGITS)
# define FIRST '0'
# define LAST '9'
# define CHARS_NAME digits
#elif defined(CHARS_LOWERCASE)
# define FIRST 'a'
# define LAST 'z'
# define CHARS_NAME lowercase
#elif defined(CHARS_UPPERCASE)
# define FIRST 'A'
# define LAST 'Z'
# define CHARS_NAME uppercase
#else
# error "choose the characters: -DCHARS_DIGITS, -DCHARS_LOWERCASE or -DCHARS_UPPERCASE"
#endif

#if defined(ORDER_UP)
# define ORDER_NAME _up
#elif defined(ORDER_DOWN)
# define ORDER_NAME _down
#else
# error "choose an order: -DORDER_UP or -DORDER_DOWN"
#endif

#if defined(STEP_ALL)
# define STEP 1
# define STEP_NAME _all
#elif defined(STEP_SKIP)
# define STEP 2
# define STEP_NAME _skip
#else
# error "choose a step: -DSTEP_ALL or -DSTEP_SKIP"
#endif

/*
** The name of the function, glued by the preprocessor: ft_print_ + digits +
** _up + _skip gives ft_print_digits_up_skip. JOIN goes through GLUE so that
** the macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c, d) a ## b ## c ## d
#define JOIN(a, b, c, d) GLUE(a, b, c, d)
#define FT_NAME JOIN(ft_print_, CHARS_NAME, ORDER_NAME, STEP_NAME)

void	FT_NAME(void)
{
	char	c;

#if defined(ORDER_UP)
	c = FIRST;
	while (c <= LAST)
	{
		write(1, &c, 1);
		c += STEP;
	}
#else
	c = LAST;
	while (c >= FIRST)
	{
		write(1, &c, 1);
		c -= STEP;
	}
#endif
}
