/*
** Reference solution of bit_flip (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DPART_PAIRS ref.c main_42pal.c
*/

#if defined(PART_EACH_HALF)
# define FT_NAME ft_reverse_each_half
#elif defined(PART_PAIRS)
# define FT_NAME ft_reverse_pairs
#elif defined(PART_MIDDLE_SIX)
# define FT_NAME ft_reverse_middle_six
#else
# error "choose a part: -DPART_EACH_HALF, -DPART_PAIRS or -DPART_MIDDLE_SIX"
#endif

/* Where the bit at place `from` (0 the lowest) goes. */
static int	place_of(int from)
{
#if defined(PART_EACH_HALF)
	return (from >= 4 ? 11 - from : 3 - from);
#elif defined(PART_PAIRS)
	return (from % 2 ? from - 1 : from + 1);
#else
	return (from == 0 || from == 7 ? from : 7 - from);
#endif
}

unsigned char	FT_NAME(unsigned char octet)
{
	unsigned char	result;
	int				from;

	result = 0;
	from = 0;
	while (from < 8)
	{
		if ((octet >> from) & 1)
			result |= 1 << place_of(from);
		from++;
	}
	return (result);
}
