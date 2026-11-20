/*
** Reference solution of say_message (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DMESSAGE_SEE_YOU -DCASE_UPPER ref.c
*/

#include <unistd.h>

#if defined(MESSAGE_GOOD_MORNING)
# define MESSAGE "Good morning!"
#elif defined(MESSAGE_FORTY_TWO)
# define MESSAGE "42 is the answer."
#elif defined(MESSAGE_SEE_YOU)
# define MESSAGE "See you soon!"
#else
# error "choose a message: -DMESSAGE_GOOD_MORNING, -DMESSAGE_FORTY_TWO or -DMESSAGE_SEE_YOU"
#endif

#if !defined(CASE_AS_IS) && !defined(CASE_UPPER)
# error "choose the case: -DCASE_AS_IS or -DCASE_UPPER"
#endif

int	main(int ac, char **av)
{
	char	*message;
	char	c;

	(void)ac;
	(void)av;
	message = MESSAGE;
	while (*message)
	{
		c = *message++;
#if defined(CASE_UPPER)
		if (c >= 'a' && c <= 'z')
			c = c - 'a' + 'A';
#endif
		write(1, &c, 1);
	}
	write(1, "\n", 1);
	return (0);
}
