/*
** Reference solution of list_drop (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LAST -DCONDITION_REPEATED ref.c main_42pal.c
** next to node.h, the header the student hands in too.
*/

#include <stdlib.h>
#include "node.h"

#if defined(WHICH_ALL)
# define WHICH_NAME all
#elif defined(WHICH_FIRST)
# define WHICH_NAME first
# define STOP_AT_FIRST 1
#elif defined(WHICH_LAST)
# define WHICH_NAME last
# define STOP_AT_FIRST 0
#else
# error "choose which nodes: -DWHICH_ALL, -DWHICH_FIRST or -DWHICH_LAST"
#endif

#if defined(CONDITION_EVEN)
# define CONDITION_NAME _even
#elif defined(CONDITION_ODD)
# define CONDITION_NAME _odd
#elif defined(CONDITION_NEGATIVE)
# define CONDITION_NAME _negative
#elif defined(CONDITION_REPEATED)
# define CONDITION_NAME _repeated
#else
# error "choose a condition: -DCONDITION_EVEN, -DCONDITION_ODD, \
-DCONDITION_NEGATIVE or -DCONDITION_REPEATED"
#endif

/*
** The name of the function, glued by the preprocessor: ft_drop_ + last +
** _repeated gives ft_drop_last_repeated. JOIN goes through GLUE so that
** the macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_drop_, WHICH_NAME, CONDITION_NAME)

#if defined(CONDITION_REPEATED)

/* True if a node from begin up to node, excluded, has the same value. */
static int	seen_before(t_node *begin, t_node *node)
{
	while (begin != node)
	{
		if (begin->value == node->value)
			return (1);
		begin = begin->next;
	}
	return (0);
}

#endif

/* True if node, in the list that starts at begin, is to be removed. */
static int	matches(t_node *begin, t_node *node)
{
#if defined(CONDITION_REPEATED)
	return (seen_before(begin, node));
#else
	(void)begin;
# if defined(CONDITION_EVEN)
	return (node->value % 2 == 0);
# elif defined(CONDITION_ODD)
	return (node->value % 2 != 0);
# else
	return (node->value < 0);
# endif
#endif
}

/*
** link is the pointer that points to the node to remove: *begin or the next
** of the node before. It is made to point to the node after, then the node
** is freed.
*/
static void	drop(t_node **link)
{
	t_node	*removed;

	removed = *link;
	*link = removed->next;
	free(removed);
}

#if defined(WHICH_ALL)

void	FT_NAME(t_node **begin)
{
	t_node	**link;

	link = begin;
	while (*link)
	{
		if (matches(*begin, *link))
			drop(link);
		else
			link = &(*link)->next;
	}
}

#else

void	FT_NAME(t_node **begin)
{
	t_node	**link;
	t_node	**found;

	found = NULL;
	link = begin;
	while (*link)
	{
		if (matches(*begin, *link))
		{
			found = link;
			if (STOP_AT_FIRST)
				break ;
		}
		link = &(*link)->next;
	}
	if (found)
		drop(found);
}

#endif
