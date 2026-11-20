/*
** Reference solution of set_find (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DKIND_PAIR ref.c main_42pal.c
*/

#include <stddef.h>

#if defined(KIND_LAST)
# define FT_NAME ft_find_last
#elif defined(KIND_FIRST_OUT)
# define FT_NAME ft_find_first_out
#elif defined(KIND_LAST_OUT)
# define FT_NAME ft_find_last_out
#elif defined(KIND_PAIR)
# define FT_NAME ft_find_pair
#else
# error "choose a kind: -DKIND_LAST, -DKIND_FIRST_OUT, -DKIND_LAST_OUT or -DKIND_PAIR"
#endif

static int	in_set(char c, char *set)
{
	while (*set)
		if (*set++ == c)
			return (1);
	return (0);
}

#if defined(KIND_FIRST_OUT)

char	*FT_NAME(char *s, char *set)
{
	while (*s)
	{
		if (!in_set(*s, set))
			return (s);
		s++;
	}
	return (NULL);
}

#elif defined(KIND_PAIR)

char	*FT_NAME(char *s, char *set)
{
	while (*s && s[1])
	{
		if (in_set(s[0], set) && in_set(s[1], set))
			return (s);
		s++;
	}
	return (NULL);
}

#else

/* last and last_out: the last character for which in_set gives WANTED. */
# if defined(KIND_LAST)
#  define WANTED 1
# else
#  define WANTED 0
# endif

char	*FT_NAME(char *s, char *set)
{
	char	*last;

	last = NULL;
	while (*s)
	{
		if (in_set(*s, set) == WANTED)
			last = s;
		s++;
	}
	return (last);
}

#endif
