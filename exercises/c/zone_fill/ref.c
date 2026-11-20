/*
** Reference solution of zone_fill (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DCONNECT_EIGHT -DMEASURE_EDGE ref.c main_42pal.c
*/

#if defined(CONNECT_FOUR)
# define CONNECT_NAME four
# define STEPS 4
#elif defined(CONNECT_EIGHT)
# define CONNECT_NAME eight
# define STEPS 8
#else
# error "choose the neighbours: -DCONNECT_FOUR or -DCONNECT_EIGHT"
#endif

#if defined(MEASURE_FILL)
# define MEASURE_NAME _fill
#elif defined(MEASURE_SIZE)
# define MEASURE_NAME _size
#elif defined(MEASURE_EDGE)
# define MEASURE_NAME _edge
#else
# error "choose a measure: -DMEASURE_FILL, -DMEASURE_SIZE or -DMEASURE_EDGE"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_zone_, CONNECT_NAME, MEASURE_NAME)

/* The grid is at most 50 by 50: the cells already in the zone. */
static int	g_seen[50][50];

typedef struct s_zone
{
	char	**grid;
	int		width;
	int		height;
	char	target;
	int		count;
}	t_zone;

/* Adds (x, y) and its neighbours of the target character to the zone. */
static void	visit(t_zone *zone, int x, int y)
{
	static int	dx[8] = {1, -1, 0, 0, 1, 1, -1, -1};
	static int	dy[8] = {0, 0, 1, -1, 1, -1, 1, -1};
	int			i;

	if (x < 0 || y < 0 || x >= zone->width || y >= zone->height || g_seen[y][x]
		|| zone->grid[y][x] != zone->target)
		return ;
	g_seen[y][x] = 1;
#if defined(MEASURE_EDGE)
	if (x == 0 || y == 0 || x == zone->width - 1 || y == zone->height - 1)
		zone->count++;
#else
	zone->count++;
#endif
	i = 0;
	while (i < STEPS)
	{
		visit(zone, x + dx[i], y + dy[i]);
		i++;
	}
}

int	FT_NAME(char **grid, int width, int height, int x, int y)
{
	t_zone	zone;
	int		i;
	int		j;

	i = -1;
	while (++i < height)
	{
		j = -1;
		while (++j < width)
			g_seen[i][j] = 0;
	}
	zone.grid = grid;
	zone.width = width;
	zone.height = height;
	zone.target = grid[y][x];
	zone.count = 0;
	visit(&zone, x, y);
#if defined(MEASURE_FILL)
	i = -1;
	while (++i < height)
	{
		j = -1;
		while (++j < width)
			if (g_seen[i][j])
				grid[i][j] = 'F';
	}
#endif
	return (zone.count);
}
