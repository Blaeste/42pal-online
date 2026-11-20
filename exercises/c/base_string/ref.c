/*
** Reference solution of base_string (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DBASE_HEX -DFORMAT_PREFIXED ref.c main_42pal.c
*/

#include <stdlib.h>

#if defined(BASE_BINARY)
# define RADIX 2
# define BASE_NAME binary
# define PREFIX "0b"
#elif defined(BASE_OCTAL)
# define RADIX 8
# define BASE_NAME octal
# define PREFIX "0o"
#elif defined(BASE_HEX)
# define RADIX 16
# define BASE_NAME hex
# define PREFIX "0x"
#else
# error "choose a base: -DBASE_BINARY, -DBASE_OCTAL or -DBASE_HEX"
#endif

#if defined(FORMAT_PLAIN)
# define FORMAT_NAME _plain
# define PREFIX_LENGTH 0
#elif defined(FORMAT_PREFIXED)
# define FORMAT_NAME _prefixed
# define PREFIX_LENGTH 2
#else
# error "choose a format: -DFORMAT_PLAIN or -DFORMAT_PREFIXED"
#endif

/*
** The name of the function, glued by the preprocessor: ft_ + hex + _string +
** _prefixed gives ft_hex_string_prefixed. JOIN goes through GLUE so that
** the macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c, d) a ## b ## c ## d
#define JOIN(a, b, c, d) GLUE(a, b, c, d)
#define FT_NAME JOIN(ft_, BASE_NAME, _string, FORMAT_NAME)

char	*FT_NAME(int n)
{
	long	value;
	char	digits[40];
	int		count;
	char	*text;
	int		i;

	/* A long, so that -(-2147483648) fits. */
	value = n;
	if (value < 0)
		value = -value;
	digits[0] = '0';
	count = (value == 0);
	while (value)
	{
		digits[count++] = "0123456789abcdef"[value % RADIX];
		value /= RADIX;
	}
	text = malloc((n < 0) + PREFIX_LENGTH + count + 1);
	if (!text)
		return (NULL);
	i = 0;
	if (n < 0)
		text[i++] = '-';
#if defined(FORMAT_PREFIXED)
	text[i++] = PREFIX[0];
	text[i++] = PREFIX[1];
#endif
	while (count)
		text[i++] = digits[--count];
	text[i] = '\0';
	return (text);
}
