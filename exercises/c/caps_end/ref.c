/*
** Reference solution of caps_start and caps_end (programs), for every variant
** of both: they only differ by the letters put in uppercase.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHICH_LAST_VOWEL -DREST_LOWER ref.c
*/

#include <unistd.h>

#if !defined(WHICH_FIRST_TWO) && !defined(WHICH_SECOND) && !defined(WHICH_FIRST_VOWEL) \
	&& !defined(WHICH_LAST_TWO) && !defined(WHICH_SECOND_LAST) && !defined(WHICH_LAST_VOWEL)
# error "choose which letters: -DWHICH_FIRST_TWO, -DWHICH_SECOND, -DWHICH_FIRST_VOWEL, \
-DWHICH_LAST_TWO, -DWHICH_SECOND_LAST or -DWHICH_LAST_VOWEL"
#endif

#if !defined(REST_LOWER) && !defined(REST_KEEP)
# error "choose the rest: -DREST_LOWER or -DREST_KEEP"
#endif

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

#if defined(WHICH_FIRST_VOWEL) || defined(WHICH_LAST_VOWEL)

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

/* True if s[i], in the word from start to end (excluded), goes in uppercase. */
static int	chosen(char *s, int start, int end, int i)
{
#if defined(WHICH_FIRST_TWO)
	(void)s;
	(void)end;
	return (i - start < 2);
#elif defined(WHICH_SECOND)
	(void)s;
	(void)end;
	return (i - start == 1);
#elif defined(WHICH_LAST_TWO)
	(void)s;
	(void)start;
	return (end - i <= 2);
#elif defined(WHICH_SECOND_LAST)
	(void)s;
	(void)start;
	return (end - i == 2);
#elif defined(WHICH_FIRST_VOWEL)
	while (start < end && !is_vowel(s[start]))
		start++;
	return (start < end && i == start);
#else
	while (end > start && !is_vowel(s[end - 1]))
		end--;
	return (end > start && i == end - 1);
#endif
}

static void	put_line(char *s)
{
	char	c;
	int		start;
	int		end;
	int		i;

	i = 0;
	while (s[i])
	{
		if (is_blank(s[i]))
		{
			write(1, &s[i++], 1);
			continue ;
		}
		start = i;
		end = i;
		while (s[end] && !is_blank(s[end]))
			end++;
		while (i < end)
		{
			c = s[i];
			if (chosen(s, start, end, i) && c >= 'a' && c <= 'z')
				c = c - 'a' + 'A';
#if defined(REST_LOWER)
			else if (!chosen(s, start, end, i) && c >= 'A' && c <= 'Z')
				c = c - 'A' + 'a';
#endif
			write(1, &c, 1);
			i++;
		}
	}
	write(1, "\n", 1);
}

int	main(int ac, char **av)
{
	int	i;

	if (ac == 1)
		write(1, "\n", 1);
	i = 1;
	while (i < ac)
		put_line(av[i++]);
	return (0);
}
