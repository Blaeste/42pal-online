/*
** Reference solution of byte_dump (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DLAYOUT_TEXT -DWIDTH_EIGHT ref.c main_42pal.c
*/

#include <stddef.h>
#include <unistd.h>

#if defined(WIDTH_EIGHT)
# define WIDTH 8
# define WIDTH_NAME eight
#elif defined(WIDTH_TWELVE)
# define WIDTH 12
# define WIDTH_NAME twelve
#else
# error "choose a width: -DWIDTH_EIGHT or -DWIDTH_TWELVE"
#endif

#if defined(LAYOUT_OFFSET)
# define LAYOUT_NAME offset_
#elif defined(LAYOUT_TEXT)
# define LAYOUT_NAME text_
#else
# error "choose a layout: -DLAYOUT_OFFSET or -DLAYOUT_TEXT"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_dump_, LAYOUT_NAME, WIDTH_NAME)

void	FT_NAME(const void *addr, size_t size);

/* n in hexadecimal, on `digits` digits. */
static void	put_hex(size_t n, int digits)
{
	char	c;

	if (digits > 1)
		put_hex(n / 16, digits - 1);
	c = "0123456789abcdef"[n % 16];
	write(1, &c, 1);
}

#if defined(LAYOUT_OFFSET)

static void	put_line(const unsigned char *bytes, size_t start, size_t size)
{
	size_t	i;

	put_hex(start, 4);
	write(1, ":", 1);
	i = start;
	while (i < size && i < start + WIDTH)
	{
		write(1, " ", 1);
		put_hex(bytes[i++], 2);
	}
	write(1, "\n", 1);
}

#else

static void	put_line(const unsigned char *bytes, size_t start, size_t size)
{
	size_t	i;

	i = start;
	while (i < start + WIDTH)
	{
		if (i < size)
		{
			put_hex(bytes[i], 2);
			write(1, " ", 1);
		}
		else
			write(1, "   ", 3);
		i++;
	}
	write(1, "|", 1);
	i = start;
	while (i < size && i < start + WIDTH)
	{
		if (bytes[i] >= ' ' && bytes[i] <= '~')
			write(1, &bytes[i], 1);
		else
			write(1, ".", 1);
		i++;
	}
	write(1, "|\n", 2);
}

#endif

void	FT_NAME(const void *addr, size_t size)
{
	size_t	start;

	start = 0;
	while (start < size)
	{
		put_line(addr, start, size);
		start += WIDTH;
	}
}
