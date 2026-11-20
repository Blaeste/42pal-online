/*
** Reference solution of list_loop (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_START ref.c main_42pal.c
** next to ring.h, the header given with the subject.
*/

#include <stddef.h>
#include "ring.h"

#if defined(WHAT_LENGTH)
# define FT_NAME ft_loop_length
#elif defined(WHAT_START)
# define FT_NAME ft_loop_start
#elif defined(WHAT_BEFORE)
# define FT_NAME ft_loop_before
#else
# error "choose what: -DWHAT_LENGTH, -DWHAT_START or -DWHAT_BEFORE"
#endif

/*
** Floyd: a slow pointer one step at a time, a fast one two steps; they meet
** in the loop if there is one. Then a pointer from the start and one from
** the meeting point, one step at a time, meet at the first node of the loop.
*/
int	FT_NAME(t_ring *begin)
{
	t_ring	*slow;
	t_ring	*fast;
	int		count;

	slow = begin;
	fast = begin;
	while (fast && fast->next)
	{
		slow = slow->next;
		fast = fast->next->next;
		if (slow == fast)
			break ;
	}
	count = 0;
	if (!fast || !fast->next)
	{
#if defined(WHAT_LENGTH)
		return (0);
#elif defined(WHAT_START)
		return (-1);
#else
		while (begin)
		{
			count++;
			begin = begin->next;
		}
		return (count);
#endif
	}
#if defined(WHAT_LENGTH)
	fast = slow->next;
	count = 1;
	while (fast != slow)
	{
		fast = fast->next;
		count++;
	}
#else
	slow = begin;
	while (slow != fast)
	{
		slow = slow->next;
		fast = fast->next;
		count++;
	}
#endif
	return (count);
}
