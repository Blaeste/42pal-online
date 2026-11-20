/*
** Reference solution of case_flip (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DACTION_SWAP -DLETTERS_WORD_STARTS ref.c
*/

#include <unistd.h>

#if !defined(ACTION_SWAP) && !defined(ACTION_UPPER) && !defined(ACTION_LOWER)
# error "choose an action: -DACTION_SWAP, -DACTION_UPPER or -DACTION_LOWER"
#endif

#if !defined(LETTERS_VOWELS) && !defined(LETTERS_CONSONANTS) \
	&& !defined(LETTERS_EVERY_OTHER) && !defined(LETTERS_WORD_STARTS)
# error "choose the letters: -DLETTERS_VOWELS, -DLETTERS_CONSONANTS, \
-DLETTERS_EVERY_OTHER or -DLETTERS_WORD_STARTS"
#endif

static int	is_letter(char c)
{
	return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'));
}

#if defined(LETTERS_VOWELS) || defined(LETTERS_CONSONANTS)

static int	is_vowel(char c)
{
	char	*vowels;

	vowels = "aeiouAEIOU";
	while (*vowels)
		if (*vowels++ == c)
			return (1);
	return (0);
}

#endif

/* The letter c changed by the action. */
static char	changed(char c)
{
#if defined(ACTION_SWAP) || defined(ACTION_LOWER)
	if (c >= 'A' && c <= 'Z')
		return (c - 'A' + 'a');
#endif
#if defined(ACTION_SWAP) || defined(ACTION_UPPER)
	if (c >= 'a' && c <= 'z')
		return (c - 'a' + 'A');
#endif
	return (c);
}

/* True if the letter text[i], the count-th letter of the text, is to change. */
static int	is_chosen(char *text, int i, int count)
{
#if defined(LETTERS_VOWELS)
	(void)count;
	return (is_vowel(text[i]));
#elif defined(LETTERS_CONSONANTS)
	(void)count;
	return (!is_vowel(text[i]));
#elif defined(LETTERS_EVERY_OTHER)
	(void)text;
	(void)i;
	return (count % 2 == 0);
#else
	(void)count;
	return (i == 0 || text[i - 1] == ' ' || text[i - 1] == '\t');
#endif
}

int	main(int ac, char **av)
{
	char	c;
	int		i;
	int		count;

	if (ac == 2)
	{
		i = 0;
		count = 0;
		while (av[1][i])
		{
			c = av[1][i];
			if (is_letter(c))
			{
				if (is_chosen(av[1], i, count))
					c = changed(c);
				count++;
			}
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
