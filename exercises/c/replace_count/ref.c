/*
** Reference solution of replace_count (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHERE_IN_RUNS ref.c main_42pal.c
*/

#if defined(WHERE_WORD_START)
# define FT_NAME ft_replace_word_start
#elif defined(WHERE_WORD_END)
# define FT_NAME ft_replace_word_end
#elif defined(WHERE_IN_RUNS)
# define FT_NAME ft_replace_in_runs
#elif defined(WHERE_INSIDE)
# define FT_NAME ft_replace_inside
#else
# error "choose where: -DWHERE_WORD_START, -DWHERE_WORD_END, -DWHERE_IN_RUNS or -DWHERE_INSIDE"
#endif

int	FT_NAME(char *str, char from, char to);

#if defined(WHERE_WORD_START) || defined(WHERE_WORD_END)

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t' || c == '\0');
}

#endif

/* Decide on the string as it was: a run keeps its places while it changes. */
int	FT_NAME(char *str, char from, char to)
{
	int		count;
	int		i;
	char	before;
	int		place;

	count = 0;
	before = '\0';
	i = 0;
	while (str[i])
	{
#if defined(WHERE_WORD_START)
		place = i == 0 || is_blank(before);
#elif defined(WHERE_WORD_END)
		place = is_blank(str[i + 1]);
#elif defined(WHERE_IN_RUNS)
		place = (i > 0 && before == from) || str[i + 1] == from;
#else
		place = i > 0 && str[i + 1] != '\0';
#endif
		before = str[i];
		(void)before;
		if (str[i] == from && place)
		{
			str[i] = to;
			count++;
		}
		i++;
	}
	return (count);
}
