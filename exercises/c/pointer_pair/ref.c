/*
** Reference solution of pointer_pair (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DOPERATION_SUM_DIFF ref.c main_42pal.c
*/

#if defined(OPERATION_ORDER_UP)
# define FT_NAME ft_order_up
#elif defined(OPERATION_ORDER_DOWN)
# define FT_NAME ft_order_down
#elif defined(OPERATION_SUM_DIFF)
# define FT_NAME ft_sum_diff
#elif defined(OPERATION_SWAP_DOUBLE)
# define FT_NAME ft_swap_double
#elif defined(OPERATION_SWAP_NEGATE)
# define FT_NAME ft_swap_negate
#else
# error "choose an operation: -DOPERATION_ORDER_UP, -DOPERATION_ORDER_DOWN, \
-DOPERATION_SUM_DIFF, -DOPERATION_SWAP_DOUBLE or -DOPERATION_SWAP_NEGATE"
#endif

void	FT_NAME(int *a, int *b)
{
	int	old_a;

	old_a = *a;
#if defined(OPERATION_ORDER_UP)
	if (*a > *b)
	{
		*a = *b;
		*b = old_a;
	}
#elif defined(OPERATION_ORDER_DOWN)
	if (*a < *b)
	{
		*a = *b;
		*b = old_a;
	}
#elif defined(OPERATION_SUM_DIFF)
	*a = old_a + *b;
	*b = old_a - *b;
#elif defined(OPERATION_SWAP_DOUBLE)
	*a = 2 * *b;
	*b = 2 * old_a;
#else
	*a = -*b;
	*b = -old_a;
#endif
}
