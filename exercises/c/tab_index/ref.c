/*
** Reference solution of tab_index (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LAST -DRULE_REPEATED ref.c main_42pal.c
*/

#include <stddef.h>

#if defined(WHICH_FIRST)
# define WHICH_NAME first
# define STOP_AT_FIRST 1
#elif defined(WHICH_LAST)
# define WHICH_NAME last
# define STOP_AT_FIRST 0
#else
# error "choose which value: -DWHICH_FIRST or -DWHICH_LAST"
#endif

/* MATCHES(i): true if tab[i] follows the rule. */
#if defined(RULE_BIGGEST)
# define RULE_NAME _biggest
# define MATCHES(i) (tab[i] == target)
#elif defined(RULE_SMALLEST)
# define RULE_NAME _smallest
# define MATCHES(i) (tab[i] == target)
#elif defined(RULE_NEGATIVE)
# define RULE_NAME _negative
# define MATCHES(i) (tab[i] < 0)
#elif defined(RULE_EVEN)
# define RULE_NAME _even
# define MATCHES(i) (tab[i] % 2 == 0)
#elif defined(RULE_REPEATED)
# define RULE_NAME _repeated
# define MATCHES(i) (seen_before(tab, i))
#else
# error "choose a rule: -DRULE_BIGGEST, -DRULE_SMALLEST, -DRULE_NEGATIVE, \
-DRULE_EVEN or -DRULE_REPEATED"
#endif

/*
** The name of the function, glued by the preprocessor: ft_index_ + last +
** _repeated gives ft_index_last_repeated. JOIN goes through GLUE so that
** the macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_index_, WHICH_NAME, RULE_NAME)

#if defined(RULE_BIGGEST) || defined(RULE_SMALLEST)

/* The biggest (or smallest) value of the array; len is at least 1. */
static int	extreme(int *tab, unsigned int len)
{
	unsigned int	i;
	int				best;

	best = tab[0];
	i = 1;
	while (i < len)
	{
# if defined(RULE_BIGGEST)
		if (tab[i] > best)
# else
		if (tab[i] < best)
# endif
			best = tab[i];
		i++;
	}
	return (best);
}

#endif
#if defined(RULE_REPEATED)

/* True if the value at index i is also at a smaller index. */
static int	seen_before(int *tab, unsigned int i)
{
	unsigned int	j;

	j = 0;
	while (j < i)
	{
		if (tab[j] == tab[i])
			return (1);
		j++;
	}
	return (0);
}

#endif

int	FT_NAME(int *tab, unsigned int len)
{
	unsigned int	i;
	int				found;
#if defined(RULE_BIGGEST) || defined(RULE_SMALLEST)
	int				target;
#endif

	if (len == 0 || tab == NULL)
		return (-1);
#if defined(RULE_BIGGEST) || defined(RULE_SMALLEST)
	target = extreme(tab, len);
#endif
	found = -1;
	i = 0;
	while (i < len)
	{
		if (MATCHES(i))
		{
			found = i;
			if (STOP_AT_FIRST)
				return (found);
		}
		i++;
	}
	return (found);
}
