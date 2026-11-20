/*
** Reference solution of step_marks (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHERE_CAPITALS ref.c main_42pal.c
*/

#if defined(WHERE_WORD_STARTS)
# define FT_NAME ft_step_word_starts
#elif defined(WHERE_WORD_ENDS)
# define FT_NAME ft_step_word_ends
#elif defined(WHERE_CAPITALS)
# define FT_NAME ft_step_capitals
#else
# error "choose where: -DWHERE_WORD_STARTS, -DWHERE_WORD_ENDS or -DWHERE_CAPITALS"
#endif

char	*FT_NAME(char *str);

static char	next(char c)
{
	if (c == 'z')
		return ('a');
	if (c == 'Z')
		return ('A');
	if ((c >= 'a' && c < 'z') || (c >= 'A' && c < 'Z'))
		return (c + 1);
	return (c);
}

#if !defined(WHERE_CAPITALS)

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t' || c == '\0');
}

#endif

char	*FT_NAME(char *str)
{
	int	i;

	i = 0;
	while (str[i])
	{
#if defined(WHERE_WORD_STARTS)
		if (!is_blank(str[i]) && (i == 0 || is_blank(str[i - 1])))
			str[i] = next(str[i]);
#elif defined(WHERE_WORD_ENDS)
		if (!is_blank(str[i]) && is_blank(str[i + 1]))
			str[i] = next(str[i]);
#else
		if (str[i] >= 'A' && str[i] <= 'Z')
			str[i] = next(str[i]);
#endif
		i++;
	}
	return (str);
}
