/*
** Reference solution of repeat_alloc (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DRULE_BY_CASE ref.c main_42pal.c
*/

#include <stdlib.h>

#if defined(RULE_VOWELS_TWICE)
# define FT_NAME ft_repeat_vowels_twice
#elif defined(RULE_BY_CASE)
# define FT_NAME ft_repeat_by_case
#elif defined(RULE_BY_INDEX)
# define FT_NAME ft_repeat_by_index
#else
# error "choose a rule: -DRULE_VOWELS_TWICE, -DRULE_BY_CASE or -DRULE_BY_INDEX"
#endif

char	*FT_NAME(char *str);

/* How many times the character c, at index i, is repeated. */
static int	times(char c, int i)
{
#if defined(RULE_VOWELS_TWICE)
	char	*vowels;

	(void)i;
	vowels = "aeiouAEIOU";
	while (*vowels)
		if (*vowels++ == c)
			return (2);
	return (1);
#elif defined(RULE_BY_CASE)
	(void)i;
	if (c >= 'A' && c <= 'Z')
		return (3);
	if (c >= 'a' && c <= 'z')
		return (2);
	return (1);
#else
	(void)c;
	return (i % 3 + 1);
#endif
}

char	*FT_NAME(char *str)
{
	char	*made;
	int		size;
	int		i;
	int		j;
	int		n;

	size = 0;
	i = -1;
	while (str[++i])
		size += times(str[i], i);
	made = malloc(size + 1);
	if (!made)
		return (NULL);
	j = 0;
	i = -1;
	while (str[++i])
	{
		n = times(str[i], i);
		while (n-- > 0)
			made[j++] = str[i];
	}
	made[j] = '\0';
	return (made);
}
