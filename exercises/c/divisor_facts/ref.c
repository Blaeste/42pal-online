/*
** Reference solution of divisor_facts (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_EUCLID_STEPS ref.c
*/

#include <unistd.h>

#if !defined(WHAT_COMMON_COUNT) && !defined(WHAT_COMMON_LIST) && !defined(WHAT_COPRIME) \
	&& !defined(WHAT_EUCLID_STEPS)
# error "choose what: -DWHAT_COMMON_COUNT, -DWHAT_COMMON_LIST, -DWHAT_COPRIME \
or -DWHAT_EUCLID_STEPS"
#endif

/* Each helper only where the variant uses it: -Werror refuses the others. */
#if !defined(WHAT_COPRIME)

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

#endif

/* The number in str: digits only, 1 to 7 of them, more than 0; or 0. */
static int	read_number(char *str)
{
	int	n;
	int	length;

	n = 0;
	length = 0;
	while (str[length])
	{
		if (str[length] < '0' || str[length] > '9' || length >= 7)
			return (0);
		n = n * 10 + (str[length++] - '0');
	}
	return (n);
}

#if !defined(WHAT_EUCLID_STEPS)

static int	gcd(int a, int b)
{
	int	r;

	while (b)
	{
		r = a % b;
		a = b;
		b = r;
	}
	return (a);
}

#endif

int	main(int ac, char **av)
{
	int	a;
	int	b;
	int	d;
	int	count;

	a = (ac == 3) ? read_number(av[1]) : 0;
	b = (ac == 3) ? read_number(av[2]) : 0;
	if (a > 0 && b > 0)
	{
		(void)d;
		(void)count;
#if defined(WHAT_COMMON_COUNT) || defined(WHAT_COMMON_LIST)
		count = 0;
		d = 1;
		while (d <= gcd(a, b))
		{
			if (gcd(a, b) % d == 0)
			{
# if defined(WHAT_COMMON_LIST)
				if (count > 0)
					write(1, " ", 1);
				put_number(d);
# endif
				count++;
			}
			d++;
		}
# if defined(WHAT_COMMON_COUNT)
		put_number(count);
# endif
#elif defined(WHAT_COPRIME)
		if (gcd(a, b) == 1)
			write(1, "yes", 3);
		else
			write(1, "no", 2);
#else
		put_number(a);
		write(1, " ", 1);
		put_number(b);
		while (a % b)
		{
			d = a % b;
			a = b;
			b = d;
			write(1, " ", 1);
			put_number(b);
		}
#endif
	}
	write(1, "\n", 1);
	return (0);
}
