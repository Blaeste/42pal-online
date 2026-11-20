/*
** Reference solution of word_join (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DJOINT_COMMA -DCASE_LOWER ref.c
*/

#include <unistd.h>

#if defined(JOINT_DASH)
# define JOINT "-"
#elif defined(JOINT_DOT)
# define JOINT "."
#elif defined(JOINT_COMMA)
# define JOINT ", "
#elif defined(JOINT_NEWLINE)
# define JOINT "\n"
#else
# error "choose a joint: -DJOINT_DASH, -DJOINT_DOT, -DJOINT_COMMA or -DJOINT_NEWLINE"
#endif

#if !defined(CASE_KEEP) && !defined(CASE_LOWER)
# error "choose the case: -DCASE_KEEP or -DCASE_LOWER"
#endif

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

int	main(int ac, char **av)
{
	char	*joint;
	char	c;
	int		words;
	int		i;

	if (ac == 2)
	{
		words = 0;
		i = 0;
		while (av[1][i])
		{
			while (is_blank(av[1][i]))
				i++;
			if (!av[1][i])
				break ;
			joint = JOINT;
			while (words > 0 && *joint)
				write(1, joint++, 1);
			while (av[1][i] && !is_blank(av[1][i]))
			{
				c = av[1][i++];
#if defined(CASE_LOWER)
				if (c >= 'A' && c <= 'Z')
					c = c - 'A' + 'a';
#endif
				write(1, &c, 1);
			}
			words++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
