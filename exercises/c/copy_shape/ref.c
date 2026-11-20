/*
** Reference solution of copy_shape (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_LETTERS -DRETURNED_END ref.c main_42pal.c
*/

#if defined(WHAT_REVERSED)
# define WHAT_NAME reversed
#elif defined(WHAT_LETTERS)
# define WHAT_NAME letters
#elif defined(WHAT_UPPER)
# define WHAT_NAME upper
#elif defined(WHAT_NO_SPACES)
# define WHAT_NAME no_spaces
#else
# error "choose what to copy: -DWHAT_REVERSED, -DWHAT_LETTERS, -DWHAT_UPPER or -DWHAT_NO_SPACES"
#endif

#if defined(RETURNED_START)
# define RETURNED_NAME _start
#elif defined(RETURNED_END)
# define RETURNED_NAME _end
#else
# error "choose what to return: -DRETURNED_START or -DRETURNED_END"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_copy_, WHAT_NAME, RETURNED_NAME)

char	*FT_NAME(char *dst, char *src)
{
	int	i;
	int	j;

	i = 0;
	j = 0;
#if defined(WHAT_REVERSED)
	while (src[i])
		i++;
	while (i > 0)
		dst[j++] = src[--i];
#else
	while (src[i])
	{
# if defined(WHAT_LETTERS)
		if ((src[i] >= 'a' && src[i] <= 'z') || (src[i] >= 'A' && src[i] <= 'Z'))
			dst[j++] = src[i];
# elif defined(WHAT_UPPER)
		dst[j++] = (src[i] >= 'a' && src[i] <= 'z') ? src[i] - 'a' + 'A' : src[i];
# else
		if (src[i] != ' ')
			dst[j++] = src[i];
# endif
		i++;
	}
#endif
	dst[j] = '\0';
#if defined(RETURNED_END)
	return (dst + j);
#else
	return (dst);
#endif
}
