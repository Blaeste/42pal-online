/*
** Reference solution of back_print (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_EACH_LINE ref.c main_42pal.c
*/

#include <unistd.h>

#if defined(WHAT_LETTERS_ONLY)
# define FT_NAME ft_print_back_letters_only
#elif defined(WHAT_EVERY_OTHER)
# define FT_NAME ft_print_back_every_other
#elif defined(WHAT_EACH_LINE)
# define FT_NAME ft_print_back_each_line
#else
# error "choose what: -DWHAT_LETTERS_ONLY, -DWHAT_EVERY_OTHER or -DWHAT_EACH_LINE"
#endif

void	FT_NAME(char *str);

#if defined(WHAT_EACH_LINE)

void	FT_NAME(char *str)
{
	int	start;
	int	end;
	int	i;

	start = 0;
	while (1)
	{
		end = start;
		while (str[end] && str[end] != '\n')
			end++;
		i = end;
		while (i > start)
			write(1, &str[--i], 1);
		write(1, "\n", 1);
		if (!str[end])
			return ;
		start = end + 1;
	}
}

#else

void	FT_NAME(char *str)
{
	int	i;

	i = 0;
	while (str[i])
		i++;
# if defined(WHAT_EVERY_OTHER)
	i--;
	while (i >= 0)
	{
		write(1, &str[i], 1);
		i -= 2;
	}
# else
	while (i-- > 0)
		if ((str[i] >= 'a' && str[i] <= 'z') || (str[i] >= 'A' && str[i] <= 'Z'))
			write(1, &str[i], 1);
# endif
	write(1, "\n", 1);
}

#endif
