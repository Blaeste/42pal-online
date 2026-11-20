/*
** Reference solution of triple_swap (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DHOW_SORT_UP ref.c main_42pal.c
*/

#if defined(HOW_TURN_LEFT)
# define FT_NAME ft_three_turn_left
#elif defined(HOW_TURN_RIGHT)
# define FT_NAME ft_three_turn_right
#elif defined(HOW_SORT_UP)
# define FT_NAME ft_three_sort_up
#elif defined(HOW_SORT_DOWN)
# define FT_NAME ft_three_sort_down
#else
# error "choose how: -DHOW_TURN_LEFT, -DHOW_TURN_RIGHT, -DHOW_SORT_UP or -DHOW_SORT_DOWN"
#endif

void	FT_NAME(int *a, int *b, int *c);

#if defined(HOW_SORT_UP) || defined(HOW_SORT_DOWN)

/* Exchange *x and *y when they are in the wrong order. */
static void	order(int *x, int *y)
{
	int	kept;

# if defined(HOW_SORT_UP)
	if (*x <= *y)
		return ;
# else
	if (*x >= *y)
		return ;
# endif
	kept = *x;
	*x = *y;
	*y = kept;
}

void	FT_NAME(int *a, int *b, int *c)
{
	order(a, b);
	order(b, c);
	order(a, b);
}

#else

void	FT_NAME(int *a, int *b, int *c)
{
	int	kept;

# if defined(HOW_TURN_LEFT)
	kept = *a;
	*a = *b;
	*b = *c;
	*c = kept;
# else
	kept = *c;
	*c = *b;
	*b = *a;
	*a = kept;
# endif
}

#endif
