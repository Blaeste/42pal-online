/*
** Reference solution of split_fields (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSEPARATOR_COMMA -DEMPTY_KEEP ref.c main_42pal.c
*/

#include <stdlib.h>

#if defined(SEPARATOR_WHITESPACE)
# define SEPARATOR_NAME whitespace
#elif defined(SEPARATOR_COMMA)
# define SEPARATOR_NAME comma
#elif defined(SEPARATOR_COLON)
# define SEPARATOR_NAME colon
#elif defined(SEPARATOR_SEMICOLON)
# define SEPARATOR_NAME semicolon
#else
# error "choose a separator: -DSEPARATOR_WHITESPACE, _COMMA, _COLON or _SEMICOLON"
#endif

#if defined(EMPTY_SKIP)
# define EMPTY_NAME _skip
#elif defined(EMPTY_KEEP)
# define EMPTY_NAME _keep
#else
# error "choose what to do with empty fields: -DEMPTY_SKIP or -DEMPTY_KEEP"
#endif

/*
** The name of the function, glued by the preprocessor: ft_split_ + comma +
** _keep gives ft_split_comma_keep. JOIN goes through GLUE so that the
** macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_split_, SEPARATOR_NAME, EMPTY_NAME)

static int	is_separator(char c)
{
#if defined(SEPARATOR_WHITESPACE)
	return (c == ' ' || c == '\t' || c == '\n');
#elif defined(SEPARATOR_COMMA)
	return (c == ',');
#elif defined(SEPARATOR_COLON)
	return (c == ':');
#else
	return (c == ';');
#endif
}

/* keep: n separators give n + 1 fields; skip: one field per run of letters. */
static int	count_fields(char *str)
{
	int	count;
	int	i;

	count = 0;
	i = 0;
#if defined(EMPTY_KEEP)
	count = 1;
	while (str[i])
		if (is_separator(str[i++]))
			count++;
#else
	while (str[i])
	{
		if (!is_separator(str[i]) && (i == 0 || is_separator(str[i - 1])))
			count++;
		i++;
	}
#endif
	return (count);
}

/* A new string with the len first characters of start. */
static char	*copy(char *start, int len)
{
	char	*field;
	int		i;

	field = malloc(len + 1);
	if (!field)
		return (NULL);
	i = 0;
	while (i < len)
	{
		field[i] = start[i];
		i++;
	}
	field[len] = '\0';
	return (field);
}

static int	field_length(char *str)
{
	int	len;

	len = 0;
	while (str[len] && !is_separator(str[len]))
		len++;
	return (len);
}

char	**FT_NAME(char *str)
{
	char	**fields;
	int		n;
	int		len;

	fields = malloc(sizeof(char *) * (count_fields(str) + 1));
	if (!fields)
		return (NULL);
	n = 0;
#if defined(EMPTY_KEEP)
	while (1)
	{
		len = field_length(str);
		fields[n++] = copy(str, len);
		if (!str[len])
			break ;
		str += len + 1;
	}
#else
	while (*str)
	{
		while (*str && is_separator(*str))
			str++;
		if (!*str)
			break ;
		len = field_length(str);
		fields[n++] = copy(str, len);
		str += len;
	}
#endif
	fields[n] = NULL;
	return (fields);
}
