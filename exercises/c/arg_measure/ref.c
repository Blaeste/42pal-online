/*
** Reference solution of arg_measure (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_DISTINCT ref.c
*/

#include <unistd.h>

#if !defined(WHAT_TOTAL_LENGTH) && !defined(WHAT_LONGEST) && !defined(WHAT_NUMBERS) \
	&& !defined(WHAT_DISTINCT)
# error "choose what: -DWHAT_TOTAL_LENGTH, -DWHAT_LONGEST, -DWHAT_NUMBERS or -DWHAT_DISTINCT"
#endif

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

/* Each helper only where the variant uses it: -Werror refuses the others. */
#if defined(WHAT_TOTAL_LENGTH) || defined(WHAT_LONGEST)

static int	length(char *s)
{
	int	n;

	n = 0;
	while (s[n])
		n++;
	return (n);
}

#endif

#if defined(WHAT_DISTINCT)

static int	same(char *a, char *b)
{
	while (*a && *a == *b)
	{
		a++;
		b++;
	}
	return (*a == *b);
}

#endif

#if !defined(WHAT_LONGEST)

/* What argument i adds to the result. */
static int	counted(char **av, int i)
{
	int	j;

#if defined(WHAT_TOTAL_LENGTH)
	(void)j;
	return (length(av[i]));
#elif defined(WHAT_NUMBERS)
	if (!av[i][0])
		return (0);
	j = 0;
	while (av[i][j])
		if (av[i][j] < '0' || av[i][j++] > '9')
			return (0);
	return (1);
#else
	j = 1;
	while (j < i)
		if (same(av[j++], av[i]))
			return (0);
	return (1);
#endif
}

#endif

int	main(int ac, char **av)
{
	int	result;
	int	i;

	result = 0;
	i = 1;
	while (i < ac)
	{
#if defined(WHAT_LONGEST)
		if (length(av[i]) > result)
			result = length(av[i]);
#else
		result += counted(av, i);
#endif
		i++;
	}
	put_number(result);
	write(1, "\n", 1);
	return (0);
}
