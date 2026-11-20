/*
** Reference solution of len_kinds (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_WORDS ref.c main_42pal.c
*/

#if defined(WHAT_WORDS)
# define FT_NAME ft_len_words
#elif defined(WHAT_LONGEST_WORD)
# define FT_NAME ft_len_longest_word
#elif defined(WHAT_NO_SPACES)
# define FT_NAME ft_len_no_spaces
#elif defined(WHAT_UNTIL_DIGIT)
# define FT_NAME ft_len_until_digit
#else
# error "choose what: -DWHAT_WORDS, -DWHAT_LONGEST_WORD, -DWHAT_NO_SPACES or -DWHAT_UNTIL_DIGIT"
#endif

int	FT_NAME(char *str);

#if defined(WHAT_UNTIL_DIGIT)

int	FT_NAME(char *str)
{
	int	i;

	i = 0;
	while (str[i] && !(str[i] >= '0' && str[i] <= '9'))
		i++;
	return (i);
}

#else

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

int	FT_NAME(char *str)
{
	int	result;
	int	length;
	int	i;

	result = 0;
	i = 0;
	while (str[i])
	{
		while (is_blank(str[i]))
			i++;
		length = 0;
		while (str[i + length] && !is_blank(str[i + length]))
			length++;
		if (length == 0)
			break ;
# if defined(WHAT_WORDS)
		result++;
# elif defined(WHAT_LONGEST_WORD)
		if (length > result)
			result = length;
# else
		result += length;
# endif
		i += length;
	}
	return (result);
}

#endif
