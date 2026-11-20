/*
** Reference solution of span_set (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSET_VOWELS -DSIDE_END ref.c main_42pal.c
*/

#include <stddef.h>

#if defined(SET_DIGITS)
# define SET_NAME digits
# define IN_SET(c) ((c) >= '0' && (c) <= '9')
#elif defined(SET_LETTERS)
# define SET_NAME letters
# define IN_SET(c) (((c) >= 'a' && (c) <= 'z') || ((c) >= 'A' && (c) <= 'Z'))
#elif defined(SET_BLANKS)
# define SET_NAME blanks
# define IN_SET(c) ((c) == ' ' || (c) == '\t')
#elif defined(SET_VOWELS)
# define SET_NAME vowels
# define IN_SET(c) (is_vowel(c))
#else
# error "choose a set: -DSET_DIGITS, -DSET_LETTERS, -DSET_BLANKS or -DSET_VOWELS"
#endif

#if defined(SIDE_START)
# define SIDE_NAME _start
#elif defined(SIDE_END)
# define SIDE_NAME _end
#else
# error "choose a side: -DSIDE_START or -DSIDE_END"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_span_, SET_NAME, SIDE_NAME)

#if defined(SET_VOWELS)

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

size_t	FT_NAME(char *s)
{
	size_t	count;
	size_t	length;

	length = 0;
	while (s[length])
		length++;
	count = 0;
#if defined(SIDE_START)
	while (count < length && IN_SET(s[count]))
		count++;
#else
	while (count < length && IN_SET(s[length - 1 - count]))
		count++;
#endif
	return (count);
}
