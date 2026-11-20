/*
** Reference solution of case_zone (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DZONE_IN_BRACKETS ref.c main_42pal.c
*/

#if defined(ZONE_FIRST_HALF)
# define FT_NAME ft_swapcase_first_half
#elif defined(ZONE_ODD_WORDS)
# define FT_NAME ft_swapcase_odd_words
#elif defined(ZONE_AFTER_DIGIT)
# define FT_NAME ft_swapcase_after_digit
#elif defined(ZONE_IN_BRACKETS)
# define FT_NAME ft_swapcase_in_brackets
#else
# error "choose a zone: -DZONE_FIRST_HALF, -DZONE_ODD_WORDS, -DZONE_AFTER_DIGIT or -DZONE_IN_BRACKETS"
#endif

char	*FT_NAME(char *str);

static char	swapped(char c)
{
	if (c >= 'a' && c <= 'z')
		return (c - 'a' + 'A');
	if (c >= 'A' && c <= 'Z')
		return (c - 'A' + 'a');
	return (c);
}

char	*FT_NAME(char *str)
{
	int	i;
	int	in_zone;
#if defined(ZONE_FIRST_HALF)
	int	length;

	length = 0;
	while (str[length])
		length++;
#elif defined(ZONE_ODD_WORDS)
	int	words;

	words = 0;
#endif
	in_zone = 0;
	i = 0;
	while (str[i])
	{
#if defined(ZONE_FIRST_HALF)
		in_zone = i < length / 2;
#elif defined(ZONE_ODD_WORDS)
		if (str[i] != ' ' && str[i] != '\t' && (i == 0 || str[i - 1] == ' ' || str[i - 1] == '\t'))
			words++;
		in_zone = str[i] != ' ' && str[i] != '\t' && words % 2 == 1;
#elif defined(ZONE_AFTER_DIGIT)
		in_zone = i > 0 && str[i - 1] >= '0' && str[i - 1] <= '9';
#else
		if (str[i] == '(')
			in_zone = 1;
		else if (str[i] == ')')
			in_zone = 0;
#endif
		if (in_zone)
			str[i] = swapped(str[i]);
		i++;
	}
	return (str);
}
