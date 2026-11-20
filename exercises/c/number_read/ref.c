/*
** Reference solution of number_read (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DBASE_HEX -DFORMAT_GROUPED ref.c main_42pal.c
*/

#if defined(BASE_BINARY)
# define RADIX 2
# define BASE_NAME binary
# define PREFIX_LETTER 'b'
#elif defined(BASE_OCTAL)
# define RADIX 8
# define BASE_NAME octal
# define PREFIX_LETTER 'o'
#elif defined(BASE_DECIMAL)
# define RADIX 10
# define BASE_NAME decimal
#elif defined(BASE_HEX)
# define RADIX 16
# define BASE_NAME hex
# define PREFIX_LETTER 'x'
#else
# error "choose a base: -DBASE_BINARY, -DBASE_OCTAL, -DBASE_DECIMAL or -DBASE_HEX"
#endif

#if defined(FORMAT_PLAIN)
# define FORMAT_NAME _plain
#elif defined(FORMAT_PREFIXED)
# define FORMAT_NAME _prefixed
#elif defined(FORMAT_GROUPED)
# define FORMAT_NAME _grouped
#else
# error "choose a format: -DFORMAT_PLAIN, -DFORMAT_PREFIXED or -DFORMAT_GROUPED"
#endif

/*
** The name of the function, glued by the preprocessor: ft_read_ + hex +
** _grouped gives ft_read_hex_grouped. JOIN goes through GLUE so that the
** macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_read_, BASE_NAME, FORMAT_NAME)

/* The value of c as a digit of the base, or -1 if it is not one. */
static int	digit_value(char c)
{
	int	value;

	value = -1;
	if (c >= '0' && c <= '9')
		value = c - '0';
	else if (c >= 'a' && c <= 'f')
		value = c - 'a' + 10;
	else if (c >= 'A' && c <= 'F')
		value = c - 'A' + 10;
	if (value >= RADIX)
		return (-1);
	return (value);
}

int	FT_NAME(char *str)
{
	int	sign;
	int	result;
	int	digits;
	int	i;

	sign = 1;
	result = 0;
	digits = 0;
	i = 0;
	if (str[i] == '-')
	{
		sign = -1;
		i++;
	}
#if defined(FORMAT_PREFIXED)
	if (str[i] != '0' || str[i + 1] != PREFIX_LETTER)
		return (0);
	i += 2;
#endif
	while (str[i])
	{
#if defined(FORMAT_GROUPED)
		/* An underscore stands between two digits, never at an end. */
		if (str[i] == '_')
		{
			if (digits == 0 || str[i - 1] == '_' || digit_value(str[i + 1]) < 0)
				return (0);
			i++;
			continue ;
		}
#endif
		if (digit_value(str[i]) < 0)
			return (0);
		result = result * RADIX + digit_value(str[i]);
		digits++;
		i++;
	}
	if (digits == 0)
		return (0);
	return (sign * result);
}
