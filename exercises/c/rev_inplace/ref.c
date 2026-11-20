/*
** Reference solution of rev_inplace (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DPART_INNER ref.c main_42pal.c
*/

#if defined(PART_EACH_WORD)
# define FT_NAME ft_rev_each_word
#elif defined(PART_LETTERS_ONLY)
# define FT_NAME ft_rev_letters_only
#elif defined(PART_HALVES)
# define FT_NAME ft_rev_halves
#elif defined(PART_INNER)
# define FT_NAME ft_rev_inner
#else
# error "choose a part: -DPART_EACH_WORD, -DPART_LETTERS_ONLY, -DPART_HALVES or -DPART_INNER"
#endif

#if !defined(PART_LETTERS_ONLY)

/* Turns around str[start] to str[end], end included. */
static void	turn(char *str, int start, int end)
{
	char	c;

	while (start < end)
	{
		c = str[start];
		str[start++] = str[end];
		str[end--] = c;
	}
}

#endif
#if defined(PART_LETTERS_ONLY)

static int	is_letter(char c)
{
	return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'));
}

#endif

char	*FT_NAME(char *str)
{
	int		length;
	int		start;
	int		end;
	char	c;

	length = 0;
	while (str[length])
		length++;
	(void)start;
	(void)end;
	(void)c;
#if defined(PART_EACH_WORD)
	start = 0;
	while (start < length)
	{
		while (start < length && (str[start] == ' ' || str[start] == '\t'))
			start++;
		end = start;
		while (end < length && str[end] != ' ' && str[end] != '\t')
			end++;
		turn(str, start, end - 1);
		start = end;
	}
#elif defined(PART_LETTERS_ONLY)
	start = 0;
	end = length - 1;
	while (start < end)
	{
		if (!is_letter(str[start]))
			start++;
		else if (!is_letter(str[end]))
			end--;
		else
		{
			c = str[start];
			str[start++] = str[end];
			str[end--] = c;
		}
	}
#elif defined(PART_HALVES)
	turn(str, 0, length / 2 - 1);
	turn(str, length / 2, length - 1);
	turn(str, 0, length - 1);
#else
	if (length > 2)
		turn(str, 1, length - 2);
#endif
	return (str);
}
