/*
** Reference solution of hidden_trace (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWHAT_WINDOW -DCASE_ANY_CASE ref.c
*/

#include <unistd.h>

#if !defined(WHAT_POSITIONS) && !defined(WHAT_WINDOW) && !defined(WHAT_BACKWARDS)
# error "choose what: -DWHAT_POSITIONS, -DWHAT_WINDOW or -DWHAT_BACKWARDS"
#endif

#if !defined(CASE_EXACT) && !defined(CASE_ANY_CASE)
# error "choose the case: -DCASE_EXACT or -DCASE_ANY_CASE"
#endif

/* Each helper only where the variant uses it: -Werror refuses the others. */
#if !defined(WHAT_BACKWARDS)

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

#endif

static int	same(char a, char b)
{
#if defined(CASE_ANY_CASE)
	if (a >= 'A' && a <= 'Z')
		a = a - 'A' + 'a';
	if (b >= 'A' && b <= 'Z')
		b = b - 'A' + 'a';
#endif
	return (a == b);
}

#if !defined(WHAT_WINDOW)

static int	length(char *s)
{
	int	n;

	n = 0;
	while (s[n])
		n++;
	return (n);
}

#endif
#if !defined(WHAT_BACKWARDS)

/*
** Looks for s1 in s2 from index start, each character at the first place
** after the one before. Returns the index of the last character found, or -1
** if s1 is not hidden there; places, if not NULL, gets every index.
*/
static int	find(char *s1, char *s2, int start, int *places)
{
	int	i;
	int	j;

	i = 0;
	j = start;
	while (s1[i])
	{
		while (s2[j] && !same(s2[j], s1[i]))
			j++;
		if (!s2[j])
			return (-1);
		if (places)
			places[i] = j;
		i++;
		j++;
	}
	return (j - 1);
}

#endif

int	main(int ac, char **av)
{
	int	places[4096];
	int	best;
	int	end;
	int	i;

	if (ac == 3)
	{
		(void)places;
		(void)best;
		(void)end;
		(void)i;
#if defined(WHAT_POSITIONS)
		if (av[1][0] && length(av[1]) < 4096 && find(av[1], av[2], 0, places) >= 0)
		{
			i = 0;
			while (av[1][i])
			{
				if (i > 0)
					write(1, " ", 1);
				put_number(places[i++]);
			}
		}
#elif defined(WHAT_WINDOW)
		best = 0;
		i = 0;
		while (av[1][0] && av[2][i])
		{
			if (same(av[2][i], av[1][0]))
			{
				end = find(av[1], av[2], i, NULL);
				if (end >= 0 && (best == 0 || end - i + 1 < best))
					best = end - i + 1;
			}
			i++;
		}
		put_number(best);
#else
		/* s2 read backwards: each character of s1 at the first place before. */
		end = length(av[2]);
		i = 0;
		while (av[1][i])
		{
			while (end > 0 && !same(av[2][end - 1], av[1][i]))
				end--;
			if (end == 0)
				break ;
			end--;
			i++;
		}
		write(1, av[1][i] ? "0" : "1", 1);
#endif
	}
	write(1, "\n", 1);
	return (0);
}
