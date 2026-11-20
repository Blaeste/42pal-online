/*
** Reference solution of int_to_text (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DFORMAT_SPACED ref.c main_42pal.c
*/

#include <stdlib.h>

#if defined(FORMAT_SPACED)
# define FT_NAME ft_int_to_spaced
# define SEPARATOR ' '
#elif defined(FORMAT_COMMAS)
# define FT_NAME ft_int_to_commas
# define SEPARATOR ','
#elif defined(FORMAT_SIGNED)
# define FT_NAME ft_int_to_signed
#elif defined(FORMAT_PADDED)
# define FT_NAME ft_int_to_padded
#else
# error "choose a format: -DFORMAT_SPACED, -DFORMAT_COMMAS, -DFORMAT_SIGNED or -DFORMAT_PADDED"
#endif

/* The digits of n, from the right, in digits; returns how many. */
static int	digits_of(long n, char *digits)
{
	int	count;

	count = 0;
	do
	{
		digits[count++] = '0' + n % 10;
		n /= 10;
	}
	while (n);
	return (count);
}

char	*FT_NAME(int n)
{
	char	digits[16];
	char	*text;
	long	value;
	int		count;
	int		length;
	int		i;
	int		j;

	value = n;
	if (value < 0)
		value = -value;
	count = digits_of(value, digits);
#if defined(FORMAT_PADDED)
	while (count < 6)
		digits[count++] = '0';
#endif
	length = count + (n < 0);
#if defined(FORMAT_SPACED) || defined(FORMAT_COMMAS)
	length += (count - 1) / 3;
#elif defined(FORMAT_SIGNED)
	length += (n > 0);
#endif
	text = malloc(length + 1);
	if (!text)
		return (NULL);
	j = 0;
	if (n < 0)
		text[j++] = '-';
#if defined(FORMAT_SIGNED)
	if (n > 0)
		text[j++] = '+';
#endif
	i = count;
	while (i-- > 0)
	{
		text[j++] = digits[i];
#if defined(FORMAT_SPACED) || defined(FORMAT_COMMAS)
		if (i > 0 && i % 3 == 0)
			text[j++] = SEPARATOR;
#endif
	}
	text[j] = '\0';
	return (text);
}
