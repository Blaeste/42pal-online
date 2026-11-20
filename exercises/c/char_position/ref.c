/*
** Reference solution of char_position (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DMODE_LAST -DCASE_ANY ref.c main_42pal.c
*/

#if defined(MODE_COUNT)
# define FT_NAME ft_char_count
#elif defined(MODE_FIRST)
# define FT_NAME ft_char_first
#elif defined(MODE_LAST)
# define FT_NAME ft_char_last
#else
# error "choose a mode: -DMODE_COUNT, -DMODE_FIRST or -DMODE_LAST"
#endif

#if !defined(CASE_EXACT) && !defined(CASE_ANY)
# error "choose a case: -DCASE_EXACT or -DCASE_ANY"
#endif

/* With CASE_ANY, a capital letter is compared as its lowercase. */
static char	same_case(char c)
{
#if defined(CASE_ANY)
	if (c >= 'A' && c <= 'Z')
		return (c - 'A' + 'a');
#endif
	return (c);
}

int	FT_NAME(char *str, char c)
{
	int	i;
	int	result;

#if defined(MODE_COUNT)
	result = 0;
#else
	result = -1;
#endif
	c = same_case(c);
	i = 0;
	while (str[i])
	{
		if (same_case(str[i]) == c)
		{
#if defined(MODE_COUNT)
			result++;
#elif defined(MODE_FIRST)
			return (i);
#else
			result = i;
#endif
		}
		i++;
	}
	return (result);
}
