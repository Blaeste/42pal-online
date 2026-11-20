/*
** Reference solution of repeat_rule (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DRULE_WORD_NUMBER ref.c
*/

#include <unistd.h>

#if !defined(RULE_REVERSE_RANK) && !defined(RULE_DIGIT_VALUE) && !defined(RULE_POSITION) \
	&& !defined(RULE_WORD_NUMBER) && !defined(RULE_VOWEL_RANK)
# error "choose a rule: -DRULE_REVERSE_RANK, -DRULE_DIGIT_VALUE, -DRULE_POSITION, \
-DRULE_WORD_NUMBER or -DRULE_VOWEL_RANK"
#endif

/* How many times c is displayed: place counts from 1, word too (0 for a blank). */
static int	times(char c, int place, int word)
{
#if defined(RULE_REVERSE_RANK)
	(void)place;
	(void)word;
	if (c >= 'A' && c <= 'Z')
		c = c - 'A' + 'a';
	if (c >= 'a' && c <= 'z')
		return (26 - (c - 'a'));
	return (1);
#elif defined(RULE_DIGIT_VALUE)
	(void)place;
	(void)word;
	if (c >= '0' && c <= '9')
		return (c - '0');
	return (1);
#elif defined(RULE_POSITION)
	(void)c;
	(void)word;
	return (place);
#elif defined(RULE_WORD_NUMBER)
	(void)c;
	(void)place;
	if (word == 0)
		return (1);
	return (word);
#else
	char	*vowels;
	int		rank;

	(void)place;
	(void)word;
	if (c >= 'A' && c <= 'Z')
		c = c - 'A' + 'a';
	vowels = "aeiou";
	rank = 0;
	while (vowels[rank])
	{
		if (vowels[rank] == c)
			return (rank + 1);
		rank++;
	}
	return (1);
#endif
}

int	main(int ac, char **av)
{
	int	i;
	int	word;
	int	count;

	if (ac == 2)
	{
		i = 0;
		word = 0;
		while (av[1][i])
		{
			if (av[1][i] != ' ' && av[1][i] != '\t'
				&& (i == 0 || av[1][i - 1] == ' ' || av[1][i - 1] == '\t'))
				word++;
			count = times(av[1][i], i + 1,
					(av[1][i] == ' ' || av[1][i] == '\t') ? 0 : word);
			while (count-- > 0)
				write(1, &av[1][i], 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
