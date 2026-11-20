/*
** Reference solution of board_threat (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DANSWER_WHERE -DPIECES_MIXED ref.c
*/

#include <unistd.h>

#if defined(PIECES_KNIGHTS)
# define LETTERS "N"
#elif defined(PIECES_GUARDS)
# define LETTERS "G"
#elif defined(PIECES_LINES)
# define LETTERS "L"
#elif defined(PIECES_MIXED)
# define LETTERS "NGL"
#else
# error "choose the pieces: -DPIECES_KNIGHTS, -DPIECES_GUARDS, -DPIECES_LINES or -DPIECES_MIXED"
#endif

#if !defined(ANSWER_COUNT) && !defined(ANSWER_WHERE)
# error "choose an answer: -DANSWER_COUNT or -DANSWER_WHERE"
#endif

typedef struct s_board
{
	char	**rows;
	int		height;
	int		width;
	int		target_row;
	int		target_col;
}	t_board;

static int	is_piece(char c)
{
	char	*letters;

	letters = LETTERS;
	while (*letters)
		if (*letters++ == c)
			return (1);
	return (0);
}

static void	put_number(int n)
{
	char	digit;

	if (n >= 10)
		put_number(n / 10);
	digit = '0' + n % 10;
	write(1, &digit, 1);
}

static int	distance(int a, int b)
{
	if (a > b)
		return (a - b);
	return (b - a);
}

/* From (row, col), one square after another: is T the first square not empty? */
static int	line_reaches(t_board *b, int row, int col, int step_row, int step_col)
{
	row += step_row;
	col += step_col;
	while (row >= 0 && row < b->height && col >= 0 && col < b->width)
	{
		if (b->rows[row][col] == 'T')
			return (1);
		if (is_piece(b->rows[row][col]))
			return (0);
		row += step_row;
		col += step_col;
	}
	return (0);
}

static int	attacks(t_board *b, int row, int col)
{
	int	rows_away;
	int	cols_away;

	rows_away = distance(row, b->target_row);
	cols_away = distance(col, b->target_col);
	if (b->rows[row][col] == 'N')
		return ((rows_away == 1 && cols_away == 2) || (rows_away == 2 && cols_away == 1));
	if (b->rows[row][col] == 'G')
		return (rows_away <= 1 && cols_away <= 1);
	return (line_reaches(b, row, col, 0, 1) || line_reaches(b, row, col, 0, -1)
		|| line_reaches(b, row, col, 1, 0) || line_reaches(b, row, col, -1, 0));
}

static void	find_target(t_board *b)
{
	int	row;
	int	col;

	b->target_row = 0;
	b->target_col = 0;
	row = -1;
	while (++row < b->height)
	{
		col = -1;
		while (++col < b->width)
		{
			if (b->rows[row][col] == 'T')
			{
				b->target_row = row;
				b->target_col = col;
			}
		}
	}
}

int	main(int ac, char **av)
{
	t_board	b;
	int		row;
	int		col;
	int		count;

	if (ac < 2)
		return (write(1, "\n", 1), 0);
	b.rows = av + 1;
	b.height = ac - 1;
	b.width = 0;
	while (av[1][b.width])
		b.width++;
	find_target(&b);
	count = 0;
	row = -1;
	while (++row < b.height)
	{
		col = -1;
		while (++col < b.width)
		{
			if (!is_piece(b.rows[row][col]) || !attacks(&b, row, col))
				continue ;
			count++;
#if defined(ANSWER_WHERE)
			put_number(row + 1);
			write(1, ",", 1);
			put_number(col + 1);
			write(1, "\n", 1);
#endif
		}
	}
#if defined(ANSWER_COUNT)
	put_number(count);
	write(1, "\n", 1);
#else
	if (count == 0)
		write(1, "safe\n", 5);
#endif
	return (0);
}
