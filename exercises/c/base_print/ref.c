/*
** Reference solution of base_print (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DBASE_BINARY -DFORM_GROUPED ref.c
*/

#include <unistd.h>

#if defined(BASE_BINARY)
# define RADIX 2
# define PREFIX "0b"
#elif defined(BASE_OCTAL)
# define RADIX 8
# define PREFIX "0o"
#elif defined(BASE_HEX)
# define RADIX 16
# define PREFIX "0x"
#else
# error "choose a base: -DBASE_BINARY, -DBASE_OCTAL or -DBASE_HEX"
#endif

#if !defined(FORM_PLAIN) && !defined(FORM_PREFIXED) && !defined(FORM_GROUPED)
# error "choose a form: -DFORM_PLAIN, -DFORM_PREFIXED or -DFORM_GROUPED"
#endif

int	main(int ac, char **av)
{
	char			digits[32];
	unsigned int	n;
	int				length;
	int				i;

	if (ac == 2)
	{
		n = 0;
		i = 0;
		while (av[1][i])
			n = n * 10 + (av[1][i++] - '0');
		/* The digits from the right: digits[0] is the last one. */
		length = 0;
		do
		{
			digits[length++] = "0123456789abcdef"[n % RADIX];
			n /= RADIX;
		}
		while (n);
#if defined(FORM_PREFIXED)
		write(1, PREFIX, 2);
#endif
		i = length;
		while (i-- > 0)
		{
			write(1, &digits[i], 1);
#if defined(FORM_GROUPED)
			/* i digits are left on the right: a space when they make groups of 4. */
			if (i > 0 && i % 4 == 0)
				write(1, " ", 1);
#endif
		}
	}
	write(1, "\n", 1);
	return (0);
}
