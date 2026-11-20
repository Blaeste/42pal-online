/*
** Reference solution of byte_show (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DFORM_DOTS ref.c main_42pal.c
*/

#include <unistd.h>

#if defined(FORM_LSB_FIRST)
# define FT_NAME ft_show_lsb_first
#elif defined(FORM_GROUPED)
# define FT_NAME ft_show_grouped
#elif defined(FORM_DOTS)
# define FT_NAME ft_show_dots
#elif defined(FORM_HEX)
# define FT_NAME ft_show_hex
#elif defined(FORM_OCTAL)
# define FT_NAME ft_show_octal
#else
# error "choose a form: -DFORM_LSB_FIRST, -DFORM_GROUPED, -DFORM_DOTS, -DFORM_HEX or -DFORM_OCTAL"
#endif

void	FT_NAME(unsigned char octet)
{
	char	c;
	int		i;

#if defined(FORM_HEX)
	(void)i;
	c = "0123456789abcdef"[octet / 16];
	write(1, &c, 1);
	c = "0123456789abcdef"[octet % 16];
	write(1, &c, 1);
#elif defined(FORM_OCTAL)
	(void)i;
	c = '0' + octet / 64;
	write(1, &c, 1);
	c = '0' + octet / 8 % 8;
	write(1, &c, 1);
	c = '0' + octet % 8;
	write(1, &c, 1);
#elif defined(FORM_LSB_FIRST)
	i = 0;
	while (i < 8)
	{
		c = '0' + ((octet >> i) & 1);
		write(1, &c, 1);
		i++;
	}
#else
	i = 8;
	while (i--)
	{
# if defined(FORM_DOTS)
		c = ((octet >> i) & 1) ? '#' : '.';
# else
		c = '0' + ((octet >> i) & 1);
		if (i == 3)
			write(1, " ", 1);
# endif
		write(1, &c, 1);
	}
#endif
}
