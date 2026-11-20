/*
** Reference solution of list_sort_by (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DKEY_PARITY -DORDER_DOWN ref.c main_42pal.c
** next to item.h, the header given with the subject.
*/

#include <stddef.h>
#include "item.h"

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

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_list_sort_, KEY_NAME, ORDER_NAME)

#if !defined(KEY_PARITY)

static int	absolute(int n)
{
	if (n < 0)
		return (-n);
	return (n);
}

#endif

/* The place of n in the order of the key, before the value breaks the ties. */
static int	rank(int n)
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

/* True if a must come before b in the list. */
static int	before(int a, int b)
{
#if defined(ORDER_DOWN)
	int	swap;

	swap = a;
	a = b;
	b = swap;
#endif
	if (rank(a) != rank(b))
		return (rank(a) < rank(b));
	return (a < b);
}

/* An insertion sort: each item is taken out, then put in its place. */
t_item	*FT_NAME(t_item *begin)
{
	t_item	*sorted;
	t_item	*item;
	t_item	**place;

	sorted = NULL;
	while (begin)
	{
		item = begin;
		begin = begin->next;
		place = &sorted;
		while (*place && !before(item->key, (*place)->key))
			place = &(*place)->next;
		item->next = *place;
		*place = item;
	}
	return (sorted);
}
