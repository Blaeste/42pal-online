/*
** Reference solution of tape_script (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DLOOP_COUNTDOWN -DPRINT_NUMBER ref.c
*/

#include <unistd.h>

#if defined(LOOP_TIMES)
# define OPEN '('
# define CLOSE ')'
#elif defined(LOOP_COUNTDOWN)
# define OPEN '['
# define CLOSE ']'
#elif defined(LOOP_REPEAT)
# define OPEN '{'
# define CLOSE '}'
#else
# error "choose a loop: -DLOOP_TIMES, -DLOOP_COUNTDOWN or -DLOOP_REPEAT"
#endif

#if !defined(PRINT_CHAR) && !defined(PRINT_NUMBER)
# error "choose a print: -DPRINT_CHAR or -DPRINT_NUMBER"
#endif

typedef struct s_machine
{
	char			*script;
	unsigned char	tape[64];
	int				at;
}	t_machine;

/* The index of the CLOSE that matches the OPEN at index i. */
static int	matching(char *s, int i)
{
	int	depth;

	depth = 0;
	while (s[i])
	{
		if (s[i] == OPEN)
			depth++;
		else if (s[i] == CLOSE && --depth == 0)
			return (i);
		i++;
	}
	return (i);
}

static void	show(unsigned char value)
{
#if defined(PRINT_CHAR)
	write(1, &value, 1);
#else
	char	digits[4];
	int		size;

	size = 0;
	if (value >= 100)
		digits[size++] = '0' + value / 100;
	if (value >= 10)
		digits[size++] = '0' + value / 10 % 10;
	digits[size++] = '0' + value % 10;
	digits[size++] = '\n';
	write(1, digits, size);
#endif
}

/* Run the commands from index start to index end, end excluded. */
static void	run(t_machine *m, int start, int end)
{
	int	i;
	int	close;
#if !defined(LOOP_COUNTDOWN)
	int	turns;
#endif

	i = start;
	while (i < end)
	{
		if (m->script[i] == '+')
			m->tape[m->at]++;
		else if (m->script[i] == '-')
			m->tape[m->at]--;
		else if (m->script[i] == '>')
			m->at++;
		else if (m->script[i] == '<')
			m->at--;
		else if (m->script[i] == '.')
			show(m->tape[m->at]);
		else if (m->script[i] == OPEN)
		{
			close = matching(m->script, i);
#if defined(LOOP_TIMES)
			turns = m->script[close + 1] - '0';
			while (turns-- > 0)
				run(m, i + 1, close);
			close++;
#elif defined(LOOP_COUNTDOWN)
			if (m->tape[m->at] != 0)
			{
				run(m, i + 1, close);
				while (--m->tape[m->at] != 0)
					run(m, i + 1, close);
			}
#else
			turns = m->tape[m->at];
			while (turns-- > 0)
				run(m, i + 1, close);
#endif
			i = close;
		}
		i++;
	}
}

int	main(int ac, char **av)
{
	t_machine	m;
	int			length;

	if (ac != 2)
		return (write(1, "\n", 1), 0);
	m.script = av[1];
	m.at = 0;
	length = 0;
	while (length < 64)
		m.tape[length++] = 0;
	length = 0;
	while (av[1][length])
		length++;
	run(&m, 0, length);
	return (0);
}
