/*
** Reference solution of nest_report (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DREPORT_ERROR_AT -DBRACKETS_THREE ref.c
*/

#include <unistd.h>

#if defined(BRACKETS_ROUND)
# define OPENERS "("
# define CLOSERS ")"
#elif defined(BRACKETS_THREE)
# define OPENERS "([{"
# define CLOSERS ")]}"
#elif defined(BRACKETS_FOUR)
# define OPENERS "([{<"
# define CLOSERS ")]}>"
#else
# error "choose the brackets: -DBRACKETS_ROUND, -DBRACKETS_THREE or -DBRACKETS_FOUR"
#endif

#if !defined(REPORT_DEPTH) && !defined(REPORT_ERROR_AT) && !defined(REPORT_COMPLETE)
# error "choose a report: -DREPORT_DEPTH, -DREPORT_ERROR_AT or -DREPORT_COMPLETE"
#endif

/* A string has at most 1000 characters: the stack never holds more. */
#define STACK_SIZE 1024

static void	put_str(char *text)
{
	while (*text)
		write(1, text++, 1);
}

#if !defined(REPORT_COMPLETE)

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

#endif

/* The kind of the bracket c in `set` (its index), or -1 if it is not one. */
static int	kind_in(char c, char *set)
{
	int	i;

	i = 0;
	while (set[i])
	{
		if (set[i] == c)
			return (i);
		i++;
	}
	return (-1);
}

/*
** Reads the brackets of text. kinds and places are the stack: the kind and
** the index of each bracket still open, the last opened at the top.
*/
static void	report(char *text)
{
	int	kinds[STACK_SIZE];
	int	places[STACK_SIZE];
	int	top;
	int	depth;
	int	i;

	top = 0;
	depth = 0;
	i = 0;
	while (text[i])
	{
		if (kind_in(text[i], OPENERS) >= 0)
		{
			kinds[top] = kind_in(text[i], OPENERS);
			places[top++] = i;
			if (top > depth)
				depth = top;
		}
		else if (kind_in(text[i], CLOSERS) >= 0)
		{
			if (top == 0 || kinds[top - 1] != kind_in(text[i], CLOSERS))
			{
#if defined(REPORT_ERROR_AT)
				put_number(i);
#else
				put_str("Error");
#endif
				return ;
			}
			top--;
		}
		i++;
	}
#if defined(REPORT_DEPTH)
	(void)places;
	if (top > 0)
		put_str("Error");
	else
		put_number(depth);
#elif defined(REPORT_ERROR_AT)
	if (top > 0)
		put_number(places[top - 1]);
	else
		put_str("OK");
#else
	(void)places;
	put_str(text);
	while (top > 0)
		write(1, &CLOSERS[kinds[--top]], 1);
#endif
}

int	main(int ac, char **av)
{
	int	i;

	if (ac == 1)
		write(1, "\n", 1);
	i = 1;
	while (i < ac)
	{
		report(av[i]);
		write(1, "\n", 1);
		i++;
	}
	return (0);
}
