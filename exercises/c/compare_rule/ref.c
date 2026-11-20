/*
** Reference solution of compare_rule (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DRULE_FROM_END -DRESULT_SIGN ref.c main_42pal.c
*/

#if defined(RULE_ANY_CASE)
# define RULE_NAME any_case
#elif defined(RULE_FROM_END)
# define RULE_NAME from_end
#elif defined(RULE_LENGTH_FIRST)
# define RULE_NAME length_first
#elif defined(RULE_SKIP_SPACES)
# define RULE_NAME skip_spaces
#else
# error "choose a rule: -DRULE_ANY_CASE, -DRULE_FROM_END, -DRULE_LENGTH_FIRST or -DRULE_SKIP_SPACES"
#endif

#if defined(RESULT_SIGN)
# define RESULT_NAME _sign
#elif defined(RESULT_DIFFERENCE)
# define RESULT_NAME _difference
#else
# error "choose a result: -DRESULT_SIGN or -DRESULT_DIFFERENCE"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_compare_, RULE_NAME, RESULT_NAME)

#if defined(RULE_FROM_END) || defined(RULE_LENGTH_FIRST)

static int	length(char *s)
{
	int	n;

	n = 0;
	while (s[n])
		n++;
	return (n);
}

#endif

#if defined(RULE_ANY_CASE)

static int	lower(unsigned char c)
{
	if (c >= 'A' && c <= 'Z')
		return (c - 'A' + 'a');
	return (c);
}

#endif

/* The difference the rule finds between s1 and s2. */
static int	difference(char *s1, char *s2)
{
	int	i;
	int	j;
	int	x;
	int	y;

	i = 0;
	j = 0;
#if defined(RULE_FROM_END)
	i = length(s1);
	j = length(s2);
	while (i > 0 || j > 0)
	{
		x = i > 0 ? (unsigned char)s1[i - 1] : 0;
		y = j > 0 ? (unsigned char)s2[j - 1] : 0;
		if (x != y)
			return (x - y);
		i -= (i > 0);
		j -= (j > 0);
	}
	return (0);
#else
# if defined(RULE_LENGTH_FIRST)
	if (length(s1) != length(s2))
		return (length(s1) - length(s2));
# endif
	while (1)
	{
# if defined(RULE_SKIP_SPACES)
		while (s1[i] == ' ' || s1[i] == '\t')
			i++;
		while (s2[j] == ' ' || s2[j] == '\t')
			j++;
# endif
		x = (unsigned char)s1[i];
		y = (unsigned char)s2[j];
# if defined(RULE_ANY_CASE)
		x = lower(x);
		y = lower(y);
# endif
		if (x != y || x == 0)
			return (x - y);
		i++;
		j++;
	}
#endif
}

int	FT_NAME(char *s1, char *s2)
{
	int	found;

	found = difference(s1, s2);
#if defined(RESULT_SIGN)
	return ((found > 0) - (found < 0));
#else
	return (found);
#endif
}
