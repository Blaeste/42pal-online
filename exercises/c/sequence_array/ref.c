/*
** Reference solution of sequence_array (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSEQUENCE_FIBONACCI -DORDER_DOWN ref.c main_42pal.c
*/

#include <stdlib.h>

/* The k-th term, k = 0, 1, 2...; Fibonacci is built by its own loop. */
#if defined(SEQUENCE_SQUARES)
# define SEQUENCE_NAME squares
# define TERM(k) ((k) * (k))
#elif defined(SEQUENCE_TRIANGLES)
# define SEQUENCE_NAME triangles
# define TERM(k) ((k) * ((k) + 1) / 2)
#elif defined(SEQUENCE_FIBONACCI)
# define SEQUENCE_NAME fibonacci
#elif defined(SEQUENCE_ODDS)
# define SEQUENCE_NAME odds
# define TERM(k) (2 * (k) + 1)
#elif defined(SEQUENCE_POWERS_OF_TWO)
# define SEQUENCE_NAME powers_of_two
# define TERM(k) (1 << (k))
#else
# error "choose a sequence: -DSEQUENCE_SQUARES, -DSEQUENCE_TRIANGLES, \
-DSEQUENCE_FIBONACCI, -DSEQUENCE_ODDS or -DSEQUENCE_POWERS_OF_TWO"
#endif

/* Where the k-th term goes in an array of n ints. */
#if defined(ORDER_UP)
# define ORDER_NAME _up
# define INDEX(k, n) (k)
#elif defined(ORDER_DOWN)
# define ORDER_NAME _down
# define INDEX(k, n) ((n) - 1 - (k))
#else
# error "choose an order: -DORDER_UP or -DORDER_DOWN"
#endif

/*
** The name of the function, glued by the preprocessor: ft_ + fibonacci +
** _down gives ft_fibonacci_down. JOIN goes through GLUE so that the macros
** are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_, SEQUENCE_NAME, ORDER_NAME)

#if defined(SEQUENCE_FIBONACCI)

/* Each term is the sum of the two before it: 0, 1, 1, 2, 3, 5... */
static void	fill(int *numbers, int n)
{
	int	before;
	int	current;
	int	next;
	int	k;

	before = 0;
	current = 1;
	k = 0;
	while (k < n)
	{
		numbers[INDEX(k, n)] = before;
		next = before + current;
		before = current;
		current = next;
		k++;
	}
}

#else

static void	fill(int *numbers, int n)
{
	int	k;

	k = 0;
	while (k < n)
	{
		numbers[INDEX(k, n)] = TERM(k);
		k++;
	}
}

#endif

int	*FT_NAME(int n)
{
	int	*numbers;

	if (n <= 0)
		return (NULL);
	numbers = malloc(sizeof(int) * n);
	if (!numbers)
		return (NULL);
	fill(numbers, n);
	return (numbers);
}
