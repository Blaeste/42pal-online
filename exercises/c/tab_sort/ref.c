/*
** Reference solution of tab_sort (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DKEY_PARITY -DORDER_DOWN ref.c main_42pal.c
*/

#if defined(KEY_ABSOLUTE)
# define KEY_NAME absolute
#elif defined(KEY_PARITY)
# define KEY_NAME parity
#elif defined(KEY_LAST_DIGIT)
# define KEY_NAME last_digit
#elif defined(KEY_DIGIT_COUNT)
# define KEY_NAME digit_count
#else
# error "choose a key: -DKEY_ABSOLUTE, -DKEY_PARITY, -DKEY_LAST_DIGIT or -DKEY_DIGIT_COUNT"
#endif

#if defined(ORDER_UP)
# define ORDER_NAME _up
#elif defined(ORDER_DOWN)
# define ORDER_NAME _down
#else
# error "choose an order: -DORDER_UP or -DORDER_DOWN"
#endif

/*
** The name of the function, glued by the preprocessor: ft_sort_by_ + parity
** + _down gives ft_sort_by_parity_down. JOIN goes through GLUE so that the
** macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_sort_by_, KEY_NAME, ORDER_NAME)

#if !defined(KEY_PARITY)

/* Only where the key uses it: -Werror refuses an unused function. */
static int	absolute(int n)
{
	if (n < 0)
		return (-n);
	return (n);
}

#endif

/* The place of n in the order, before the value breaks the ties. */
static int	key(int n)
{
#if defined(KEY_ABSOLUTE)
	return (absolute(n));
#elif defined(KEY_PARITY)
	return (n % 2 != 0);
#elif defined(KEY_LAST_DIGIT)
	return (absolute(n) % 10);
#else
	int	digits;

	digits = 1;
	n = absolute(n);
	while (n >= 10)
	{
		n /= 10;
		digits++;
	}
	return (digits);
#endif
}

/* True if a comes before b in the order of the key, in that order (up). */
static int	comes_before(int a, int b)
{
	if (key(a) != key(b))
		return (key(a) < key(b));
	return (a < b);
}

/* An insertion sort: each value goes back until it is in its place. */
void	FT_NAME(int *tab, unsigned int size)
{
	unsigned int	i;
	unsigned int	j;
	int				value;

	i = 1;
	while (i < size)
	{
		value = tab[i];
		j = i;
#if defined(ORDER_UP)
		while (j > 0 && comes_before(value, tab[j - 1]))
#else
		while (j > 0 && comes_before(tab[j - 1], value))
#endif
		{
			tab[j] = tab[j - 1];
			j--;
		}
		tab[j] = value;
		i++;
	}
}
