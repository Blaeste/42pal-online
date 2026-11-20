/*
** Reference solution of byte_rotate (a function), for every variant.
** It is compiled with one -D flag per param (see Variant.defines), like
** cc -Wall -Wextra -Werror -DWAY_LEFT -DAMOUNT_3 -DINVERT_FLIP ref.c main_42pal.c
*/

#if defined(WAY_LEFT)
# define WAY_NAME left
#elif defined(WAY_RIGHT)
# define WAY_NAME right
#else
# error "choose a way: -DWAY_LEFT or -DWAY_RIGHT"
#endif

#if defined(AMOUNT_1)
# define AMOUNT 1
# define AMOUNT_NAME _1
#elif defined(AMOUNT_2)
# define AMOUNT 2
# define AMOUNT_NAME _2
#elif defined(AMOUNT_3)
# define AMOUNT 3
# define AMOUNT_NAME _3
#else
# error "choose an amount: -DAMOUNT_1, -DAMOUNT_2 or -DAMOUNT_3"
#endif

/* The bits that the xor at the end inverts: none, or all 8. */
#if defined(INVERT_KEEP)
# define INVERT_NAME _keep
# define MASK 0x00
#elif defined(INVERT_FLIP)
# define INVERT_NAME _flip
# define MASK 0xFF
#else
# error "choose an inversion: -DINVERT_KEEP or -DINVERT_FLIP"
#endif

/*
** The name of the function, glued by the preprocessor: ft_rotate_ + left +
** _3 + _flip gives ft_rotate_left_3_flip. JOIN goes through GLUE so that
** the macros are replaced by their values before being glued.
*/
#define GLUE(a, b, c, d) a ## b ## c ## d
#define JOIN(a, b, c, d) GLUE(a, b, c, d)
#define FT_NAME JOIN(ft_rotate_, WAY_NAME, AMOUNT_NAME, INVERT_NAME)

/*
** The bits pushed out on one side by the first shift are brought back on
** the other side by the second one, shifted by the 8 - AMOUNT other bits.
*/
unsigned char	FT_NAME(unsigned char octet)
{
	unsigned char	rotated;

#if defined(WAY_LEFT)
	rotated = (unsigned char)((octet << AMOUNT) | (octet >> (8 - AMOUNT)));
#else
	rotated = (unsigned char)((octet >> AMOUNT) | (octet << (8 - AMOUNT)));
#endif
	return ((unsigned char)(rotated ^ MASK));
}
