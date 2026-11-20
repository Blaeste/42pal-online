/*
** Reference solution of bit_check (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DPROPERTY_ALTERNATING ref.c main_42pal.c
*/

#if defined(PROPERTY_POWER_OF_4)
# define FT_NAME ft_is_power_of_4
#elif defined(PROPERTY_ALL_ONES)
# define FT_NAME ft_is_all_ones
#elif defined(PROPERTY_ALTERNATING)
# define FT_NAME ft_is_alternating
#elif defined(PROPERTY_BIT_PALINDROME)
# define FT_NAME ft_is_bit_palindrome
#elif defined(PROPERTY_TWO_ONES)
# define FT_NAME ft_is_two_ones
#else
# error "choose a property: -DPROPERTY_POWER_OF_4, -DPROPERTY_ALL_ONES, \
-DPROPERTY_ALTERNATING, -DPROPERTY_BIT_PALINDROME or -DPROPERTY_TWO_ONES"
#endif

/* The number of bits of n, without the zeros on the left. */
static int	width(unsigned int n)
{
	int	bits;

	bits = 0;
	while (n)
	{
		bits++;
		n >>= 1;
	}
	return (bits);
}

int	FT_NAME(unsigned int n)
{
	int	bits;
	int	i;

	if (n == 0)
		return (0);
	bits = width(n);
	(void)i;
	(void)bits;
#if defined(PROPERTY_POWER_OF_4)
	return ((n & (n - 1)) == 0 && (bits - 1) % 2 == 0);
#elif defined(PROPERTY_ALL_ONES)
	return ((n & (n + 1)) == 0);
#elif defined(PROPERTY_ALTERNATING)
	i = 1;
	while (i < bits)
	{
		if (((n >> i) & 1) == ((n >> (i - 1)) & 1))
			return (0);
		i++;
	}
	return (1);
#elif defined(PROPERTY_BIT_PALINDROME)
	i = 0;
	while (i < bits / 2)
	{
		if (((n >> i) & 1) != ((n >> (bits - 1 - i)) & 1))
			return (0);
		i++;
	}
	return (1);
#else
	i = 0;
	while (n)
	{
		i += n & 1;
		n >>= 1;
	}
	(void)bits;
	return (i == 2);
#endif
}
