/*
** Reference solution of rev_part (a program), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DPART_HALVES ref.c
*/

#include <unistd.h>

#if !defined(PART_EACH_WORD) && !defined(PART_LETTERS_ONLY) && !defined(PART_HALVES) \
	&& !defined(PART_PAIRS) && !defined(PART_ODD_PLACES)
# error "choose a part: -DPART_EACH_WORD, -DPART_LETTERS_ONLY, -DPART_HALVES, \
-DPART_PAIRS or -DPART_ODD_PLACES"
#endif

static void	swap(char *a, char *b)
{
	char	c;

	c = *a;
	*a = *b;
	*b = c;
}

#if defined(PART_EACH_WORD)

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

#elif defined(PART_LETTERS_ONLY)

static int	is_letter(char c)
{
	return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'));
}

#endif

/* Turns text around in place, as the variant asks; length is its length. */
static void	turn(char *text, int length)
{
	int	start;
	int	end;
	int	i;

#if defined(PART_EACH_WORD)
	i = 0;
	while (i < length)
	{
		while (i < length && is_blank(text[i]))
			i++;
		start = i;
		while (i < length && !is_blank(text[i]))
			i++;
		end = i - 1;
		while (start < end)
			swap(&text[start++], &text[end--]);
	}
#elif defined(PART_LETTERS_ONLY)
	start = 0;
	end = length - 1;
	while (start < end)
	{
		if (!is_letter(text[start]))
			start++;
		else if (!is_letter(text[end]))
			end--;
		else
			swap(&text[start++], &text[end--]);
	}
	(void)i;
#elif defined(PART_HALVES)
	/* Turning each half around, then the whole, swaps the two halves. */
	i = length / 2;
	start = 0;
	end = i - 1;
	while (start < end)
		swap(&text[start++], &text[end--]);
	start = i;
	end = length - 1;
	while (start < end)
		swap(&text[start++], &text[end--]);
	start = 0;
	end = length - 1;
	while (start < end)
		swap(&text[start++], &text[end--]);
#elif defined(PART_PAIRS)
	i = 0;
	while (i + 1 < length)
	{
		swap(&text[i], &text[i + 1]);
		i += 2;
	}
	(void)start;
	(void)end;
#else
	start = 0;
	end = (length - 1) - (length - 1) % 2;
	while (start < end)
	{
		swap(&text[start], &text[end]);
		start += 2;
		end -= 2;
	}
	(void)i;
#endif
}

int	main(int ac, char **av)
{
	int	length;

	if (ac == 2)
	{
		length = 0;
		while (av[1][length])
			length++;
		turn(av[1], length);
		write(1, av[1], length);
	}
	write(1, "\n", 1);
	return (0);
}
