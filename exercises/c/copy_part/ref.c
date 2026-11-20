/*
** Reference solution of copy_part (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DHOW_LAST_N ref.c main_42pal.c
*/

#if defined(HOW_FIRST_N)
# define FT_NAME ft_copy_first_n
#elif defined(HOW_LAST_N)
# define FT_NAME ft_copy_last_n
#elif defined(HOW_FROM_N)
# define FT_NAME ft_copy_from_n
#else
# error "choose how: -DHOW_FIRST_N, -DHOW_LAST_N or -DHOW_FROM_N"
#endif

char	*FT_NAME(char *dst, char *src, int n);

char	*FT_NAME(char *dst, char *src, int n)
{
	int	length;
	int	start;
	int	end;
	int	i;

	length = 0;
	while (src[length])
		length++;
	start = 0;
	end = length;
#if defined(HOW_FIRST_N)
	if (n < length)
		end = n;
#elif defined(HOW_LAST_N)
	if (n < length)
		start = length - n;
#else
	start = n < length ? n : length;
#endif
	i = 0;
	while (start + i < end)
	{
		dst[i] = src[start + i];
		i++;
	}
	dst[i] = '\0';
	return (dst);
}
