/*
** Reference solution of set_run (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DKIND_LONGEST ref.c main_42pal.c
*/

#include <stddef.h>

#if defined(KIND_END)
# define FT_NAME ft_accept_end
#elif defined(KIND_LONGEST)
# define FT_NAME ft_accept_longest
#elif defined(KIND_FIRST)
# define FT_NAME ft_accept_first
#elif defined(KIND_COUNT)
# define FT_NAME ft_accept_count
#else
# error "choose a kind: -DKIND_END, -DKIND_LONGEST, -DKIND_FIRST or -DKIND_COUNT"
#endif

static int	in_set(char c, char *set)
{
	while (*set)
		if (*set++ == c)
			return (1);
	return (0);
}

#if defined(KIND_END)

size_t	FT_NAME(char *s, char *set)
{
	size_t	length;
	size_t	count;

	length = 0;
	while (s[length])
		length++;
	count = 0;
	while (count < length && in_set(s[length - 1 - count], set))
		count++;
	return (count);
}

#elif defined(KIND_COUNT)

size_t	FT_NAME(char *s, char *set)
{
	size_t	count;

	count = 0;
	while (*s)
		if (in_set(*s++, set))
			count++;
	return (count);
}

#elif defined(KIND_FIRST)

size_t	FT_NAME(char *s, char *set)
{
	size_t	count;

	while (*s && !in_set(*s, set))
		s++;
	count = 0;
	while (s[count] && in_set(s[count], set))
		count++;
	return (count);
}

#else

size_t	FT_NAME(char *s, char *set)
{
	size_t	longest;
	size_t	current;

	longest = 0;
	current = 0;
	while (*s)
	{
		if (in_set(*s++, set))
			current++;
		else
			current = 0;
		if (current > longest)
			longest = current;
	}
	return (longest);
}

#endif
