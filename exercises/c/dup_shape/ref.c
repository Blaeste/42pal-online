/*
** Reference solution of dup_shape (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSHAPE_TRIMMED ref.c main_42pal.c
*/

#include <stdlib.h>

#if defined(SHAPE_REVERSED)
# define FT_NAME ft_dup_reversed
#elif defined(SHAPE_DOUBLED)
# define FT_NAME ft_dup_doubled
#elif defined(SHAPE_TWICE)
# define FT_NAME ft_dup_twice
#elif defined(SHAPE_TRIMMED)
# define FT_NAME ft_dup_trimmed
#elif defined(SHAPE_UPPER)
# define FT_NAME ft_dup_upper
#else
# error "choose a shape: -DSHAPE_REVERSED, -DSHAPE_DOUBLED, -DSHAPE_TWICE, \
-DSHAPE_TRIMMED or -DSHAPE_UPPER"
#endif

char	*FT_NAME(char *src)
{
	char	*copy;
	int		length;
	int		start;
	int		i;
	int		j;

	length = 0;
	while (src[length])
		length++;
	start = 0;
#if defined(SHAPE_TRIMMED)
	while (start < length && (src[start] == ' ' || src[start] == '\t'))
		start++;
	while (length > start && (src[length - 1] == ' ' || src[length - 1] == '\t'))
		length--;
#endif
#if defined(SHAPE_DOUBLED) || defined(SHAPE_TWICE)
	copy = malloc(2 * length + 1);
#else
	copy = malloc(length - start + 1);
#endif
	if (!copy)
		return (NULL);
	i = start;
	j = 0;
	while (i < length)
	{
#if defined(SHAPE_REVERSED)
		copy[j++] = src[length - 1 - i];
#elif defined(SHAPE_DOUBLED)
		copy[j++] = src[i];
		copy[j++] = src[i];
#elif defined(SHAPE_UPPER)
		copy[j++] = (src[i] >= 'a' && src[i] <= 'z') ? src[i] - 'a' + 'A' : src[i];
#else
		copy[j++] = src[i];
#endif
		i++;
	}
#if defined(SHAPE_TWICE)
	i = 0;
	while (i < length)
		copy[j++] = src[i++];
#endif
	copy[j] = '\0';
	return (copy);
}
