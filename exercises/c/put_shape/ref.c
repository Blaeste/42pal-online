/*
** Reference solution of put_shape (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DHOW_FRAMED ref.c main_42pal.c
*/

#include <unistd.h>

#if defined(HOW_SPACED)
# define FT_NAME ft_put_spaced
#elif defined(HOW_FRAMED)
# define FT_NAME ft_put_framed
#elif defined(HOW_WORDS_LINES)
# define FT_NAME ft_put_words_lines
#else
# error "choose how: -DHOW_SPACED, -DHOW_FRAMED or -DHOW_WORDS_LINES"
#endif

void	FT_NAME(char *str);

#if defined(HOW_WORDS_LINES)

void	FT_NAME(char *str)
{
	int	in_word;

	in_word = 0;
	while (*str)
	{
		if (*str == ' ' || *str == '\t')
		{
			if (in_word)
				write(1, "\n", 1);
			in_word = 0;
		}
		else
		{
			write(1, str, 1);
			in_word = 1;
		}
		str++;
	}
	if (in_word)
		write(1, "\n", 1);
}

#else

void	FT_NAME(char *str)
{
	int	i;

# if defined(HOW_FRAMED)
	write(1, "[", 1);
# endif
	i = 0;
	while (str[i])
	{
# if defined(HOW_SPACED)
		if (i > 0)
			write(1, " ", 1);
# endif
		write(1, &str[i], 1);
		i++;
	}
# if defined(HOW_FRAMED)
	write(1, "]", 1);
# endif
	write(1, "\n", 1);
}

#endif
