"""Practice: subjects of one theme, one after the other, with no exam around.

Like the rest of the core, this module never prints: the terminal front-end
is in pal42/cli/practice.py.
"""

from pal42.variant import draw

def draw_practice(exercises, rng, seen):
	"""Return a variant of one of `exercises`, whose id is not in `seen`.

	The exercise is drawn first, then a seed; a subject already seen
	(exo#seed in `seen`) is drawn again, so that practising brings new ones.
	"""
	while True:
		exo = rng.choice(exercises)
		variant = draw(exo, rng.randrange(2**31))
		if variant.id not in seen:
			return variant
