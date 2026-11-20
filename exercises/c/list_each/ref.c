/*
** Reference solution of list_each (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_BACKWARDS ref.c main_42pal.c
** next to box.h, the header given with the subject.
*/

#include <stddef.h>
#include "box.h"

#if defined(WHICH_EVERY_OTHER)
# define FT_NAME ft_box_each_every_other
#elif defined(WHICH_BACKWARDS)
# define FT_NAME ft_box_each_backwards
#elif defined(WHICH_WHILE_POSITIVE)
# define FT_NAME ft_box_each_while_positive
#elif defined(WHICH_FROM_SECOND)
# define FT_NAME ft_box_each_from_second
#else
# error "choose which: -DWHICH_EVERY_OTHER, -DWHICH_BACKWARDS, -DWHICH_WHILE_POSITIVE \
or -DWHICH_FROM_SECOND"
#endif

void	FT_NAME(t_box *begin, void (*f)(int *))
{
#if defined(WHICH_BACKWARDS)
	/* The rest of the list first, then this node, on the way back. */
	if (!begin)
		return ;
	FT_NAME(begin->next, f);
	f(&begin->value);
#elif defined(WHICH_EVERY_OTHER)
	while (begin)
	{
		f(&begin->value);
		begin = begin->next;
		if (begin)
			begin = begin->next;
	}
#elif defined(WHICH_WHILE_POSITIVE)
	while (begin && begin->value > 0)
	{
		f(&begin->value);
		begin = begin->next;
	}
#else
	if (begin)
		begin = begin->next;
	while (begin)
	{
		f(&begin->value);
		begin = begin->next;
	}
#endif
}
