/*
** Reference solution of shift_words (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DBY_WORD_RANK ref.c main_42pal.c
*/

#if defined(BY_WORD_RANK)
# define FT_NAME ft_rot_word_rank
#elif defined(BY_POSITION)
# define FT_NAME ft_rot_position
#elif defined(BY_WORD_LENGTH)
# define FT_NAME ft_rot_word_length
#else
# error "choose by: -DBY_WORD_RANK, -DBY_POSITION or -DBY_WORD_LENGTH"
#endif

char	*FT_NAME(char *str);

static char	shifted(char c, int steps)
{
	steps %= 26;
	if (c >= 'a' && c <= 'z')
		return ('a' + (c - 'a' + steps) % 26);
	if (c >= 'A' && c <= 'Z')
		return ('A' + (c - 'A' + steps) % 26);
	return (c);
}

#if defined(BY_POSITION)

char	*FT_NAME(char *str)
{
	int	letters;
	int	i;

	letters = 0;
	i = 0;
	while (str[i])
	{
		if ((str[i] >= 'a' && str[i] <= 'z') || (str[i] >= 'A' && str[i] <= 'Z'))
			str[i] = shifted(str[i], ++letters);
		i++;
	}
	return (str);
}

#else

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

char	*FT_NAME(char *str)
{
	int	i;
	int	length;
	int	left;
	int	rank;

	rank = 0;
	i = 0;
	while (str[i])
	{
		while (is_blank(str[i]))
			i++;
		length = 0;
		while (str[i + length] && !is_blank(str[i + length]))
			length++;
		rank++;
		left = length;
		while (left-- > 0)
		{
# if defined(BY_WORD_RANK)
			str[i] = shifted(str[i], rank);
# else
			str[i] = shifted(str[i], length);
# endif
			i++;
		}
	}
	return (str);
}

#endif
