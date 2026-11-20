/*
** Reference solution of list_measure (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DMEASURE_MAX -DCELLS_EVERY_OTHER ref.c main_42pal.c
** next to cell.h, the header given with the subject.
*/

#include "cell.h"

#if defined(MEASURE_SUM)
# define MEASURE_NAME sum
#elif defined(MEASURE_MAX)
# define MEASURE_NAME max
#elif defined(MEASURE_MIN)
# define MEASURE_NAME min
#elif defined(MEASURE_COUNT_EVEN)
# define MEASURE_NAME count_even
#elif defined(MEASURE_COUNT_NEGATIVE)
# define MEASURE_NAME count_negative
#else
# error "choose a measure: -DMEASURE_SUM, -DMEASURE_MAX, -DMEASURE_MIN, \
-DMEASURE_COUNT_EVEN or -DMEASURE_COUNT_NEGATIVE"
#endif

#if defined(CELLS_ALL)
# define CELLS_NAME _all
#elif defined(CELLS_EVERY_OTHER)
# define CELLS_NAME _every_other
#else
# error "choose the cells: -DCELLS_ALL or -DCELLS_EVERY_OTHER"
#endif

/*
** The name of the function, glued by the preprocessor: ft_list_ + max +
** _every_other gives ft_list_max_every_other. JOIN goes through GLUE so
** that the macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_list_, MEASURE_NAME, CELLS_NAME)

int	FT_NAME(t_cell *begin)
{
	int	result;
#if defined(MEASURE_MAX) || defined(MEASURE_MIN)
	int	first;

	first = 1;
#endif
	result = 0;
	while (begin)
	{
#if defined(MEASURE_SUM)
		result += begin->number;
#elif defined(MEASURE_MAX)
		if (first || begin->number > result)
			result = begin->number;
		first = 0;
#elif defined(MEASURE_MIN)
		if (first || begin->number < result)
			result = begin->number;
		first = 0;
#elif defined(MEASURE_COUNT_EVEN)
		if (begin->number % 2 == 0)
			result++;
#else
		if (begin->number < 0)
			result++;
#endif
		begin = begin->next;
#if defined(CELLS_EVERY_OTHER)
		/* One cell out of two: the one after is skipped. */
		if (begin)
			begin = begin->next;
#endif
	}
	return (result);
}
