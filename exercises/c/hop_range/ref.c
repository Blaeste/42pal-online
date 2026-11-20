/*
** Reference solution of hop_range (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DSTEP_3 -DDIRECTION_BACKWARD ref.c main_42pal.c
*/

#include <stdlib.h>

#if defined(STEP_2)
# define STEP 2
# define STEP_NAME 2
#elif defined(STEP_3)
# define STEP 3
# define STEP_NAME 3
#elif defined(STEP_5)
# define STEP 5
# define STEP_NAME 5
#else
# error "choose a step: -DSTEP_2, -DSTEP_3 or -DSTEP_5"
#endif

#if defined(DIRECTION_FORWARD)
# define DIRECTION_NAME _forward
#elif defined(DIRECTION_BACKWARD)
# define DIRECTION_NAME _backward
#else
# error "choose a direction: -DDIRECTION_FORWARD or -DDIRECTION_BACKWARD"
#endif

#define GLUE(a, b, c) a ## b ## c
#define JOIN(a, b, c) GLUE(a, b, c)
#define FT_NAME JOIN(ft_hop_, STEP_NAME, DIRECTION_NAME)

int	*FT_NAME(int start, int end)
{
	int	*numbers;
	int	first;
	int	towards;
	int	count;
	int	i;

#if defined(DIRECTION_FORWARD)
	first = start;
	towards = end;
#else
	first = end;
	towards = start;
#endif
	count = (towards >= first ? towards - first : first - towards) / STEP + 1;
	numbers = malloc(sizeof(int) * count);
	if (!numbers)
		return (NULL);
	i = 0;
	while (i < count)
	{
		numbers[i] = first + (towards >= first ? 1 : -1) * STEP * i;
		i++;
	}
	return (numbers);
}
