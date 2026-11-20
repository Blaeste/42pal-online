/*
** Reference solution of read_int (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSTART_ANYTHING -DSIGNS_MANY ref.c main_42pal.c
*/

#if defined(START_SPACES)
# define START_NAME spaces
#elif defined(START_NOTHING)
# define START_NAME nothing
#elif defined(START_ANYTHING)
# define START_NAME anything
#else
# error "choose a start: -DSTART_SPACES, -DSTART_NOTHING or -DSTART_ANYTHING"
#endif

#if defined(SIGNS_ONE)
# define SIGNS_NAME _one
#elif defined(SIGNS_MANY)
# define SIGNS_NAME _many
#elif defined(SIGNS_MINUS_ONLY)
# define SIGNS_NAME _minus_only
#else
# error "choose the signs: -DSIGNS_ONE, -DSIGNS_MANY or -DSIGNS_MINUS_ONLY"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_read_int_, START_NAME, SIGNS_NAME)

/* Reads the sign at str[*i]: returns it (1 when there is none), *i goes after it. */
static int	read_sign(char *str, int *i)
{
	int	sign;

	sign = 1;
#if defined(SIGNS_ONE)
	if (str[*i] == '+' || str[*i] == '-')
		sign = (str[(*i)++] == '-') ? -1 : 1;
#elif defined(SIGNS_MINUS_ONLY)
	if (str[*i] == '-')
	{
		sign = -1;
		(*i)++;
	}
#else
	while (str[*i] == '+' || str[*i] == '-')
		if (str[(*i)++] == '-')
			sign = -sign;
#endif
	return (sign);
}

int	FT_NAME(char *str)
{
	int	sign;
	int	value;
	int	i;
	int	after;

	i = 0;
	(void)after;
#if defined(START_SPACES)
	while (str[i] == ' ' || (str[i] >= '\t' && str[i] <= '\r'))
		i++;
#elif defined(START_ANYTHING)
	while (str[i])
	{
		after = i;
		read_sign(str, &after);
		if (str[after] >= '0' && str[after] <= '9')
			break ;
		i++;
	}
#endif
	sign = read_sign(str, &i);
	value = 0;
	while (str[i] >= '0' && str[i] <= '9')
		value = value * 10 + (str[i++] - '0');
	return (sign * value);
}
