/*
** Reference solution of prime_facts (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DMEASURE_DIGIT_SUM -DRANGE_BETWEEN ref.c
*/

#include <unistd.h>

#if !defined(MEASURE_COUNT) && !defined(MEASURE_LARGEST) && !defined(MEASURE_DIGIT_SUM)
# error "choose a measure: -DMEASURE_COUNT, -DMEASURE_LARGEST or -DMEASURE_DIGIT_SUM"
#endif

#if !defined(RANGE_UP_TO) && !defined(RANGE_BETWEEN)
# error "choose a range: -DRANGE_UP_TO or -DRANGE_BETWEEN"
#endif

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

static int	is_prime(int n)
{
	int	d;

	if (n < 2)
		return (0);
	d = 2;
	while (d * d <= n)
	{
		if (n % d == 0)
			return (0);
		d++;
	}
	return (1);
}

/* The number written in str, or 0 if it is not made of digits only. */
static int	read_number(char *str)
{
	int	n;

	n = 0;
	if (!*str)
		return (0);
	while (*str)
	{
		if (*str < '0' || *str > '9')
			return (0);
		n = n * 10 + (*str++ - '0');
	}
	return (n);
}

int	main(int ac, char **av)
{
	int	n;
	int	p;
	int	high;
	int	result;
	int	digits;

	n = (ac == 2) ? read_number(av[1]) : 0;
	result = 0;
#if defined(RANGE_UP_TO)
	p = 2;
	high = n;
#else
	p = n;
	high = 2 * n;
#endif
	while (n > 0 && p <= high)
	{
		if (is_prime(p))
		{
#if defined(MEASURE_COUNT)
			result++;
#elif defined(MEASURE_LARGEST)
			result = p;
#else
			digits = p;
			while (digits)
			{
				result += digits % 10;
				digits /= 10;
			}
#endif
		}
		p++;
	}
	(void)digits;
	put_number(result);
	write(1, "\n", 1);
	return (0);
}
