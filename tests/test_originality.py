"""Guard: no exercise of the catalog is a real 42 exam subject.

The subjects of 42pal are written by us; the real ones only told us the
themes. This test keeps it so: no variant may carry the name of a real
subject of the piscine or of the ranks, nor of the function it asks for
(only their names are listed here, never their text).

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest
from pathlib import Path

from pal42.catalog import load_catalog
from pal42.variant import Variant

# The names of the real subjects of the piscine exams and of Exam Rank 02,
# then those of the Python ranks and of their functions.
REAL_SUBJECTS = set("""
	add_prime_sum aff_a aff_first_param aff_last_param aff_z alpha_mirror
	biggest_pal brackets brainfuck camel_to_snake check_mate cycle_detector
	do_op epur_str expand_str first_word fizzbuzz flood_fill fprime ft_atoi
	ft_atoi_base ft_countdown ft_itoa ft_itoa_base ft_list_foreach
	ft_list_remove_if ft_list_size ft_print_numbers ft_putstr ft_range
	ft_rrange ft_split ft_strcmp ft_strcpy ft_strcspn ft_strdup ft_strlen
	ft_strpbrk ft_strrev ft_strspn ft_swap hello hidenp inter is_power_of_2
	last_word lcm maff_alpha maff_revalpha max only_a only_z options paramsum
	pgcd print_bits print_hex print_memory repeat_alpha rev_print rev_wstr
	reverse_bits rostring rot_13 rotone rpn_calc rstr_capitalizer
	search_and_replace snake_to_camel sort_int_tab sort_list str_capitalizer
	swap_bits tab_mult ulstr union wdmatch
""".split()) | set("""
	py_bracket_validator py_cryptic_sorter py_echo_validator py_mirror_matrix
	py_hidenp py_inter py_number_base_converter py_pattern_tracker py_anagram
	py_shadow_merge py_string_permutation_checker py_string_sculptor
	py_twist_sequence py_whisper_cipher py_array_rotation_detector
	py_constellation_mapper py_list_intersection_finder py_merge_sorted_lists
	py_palindrome_partitioner py_package_dependency_resolver
	py_sliding_window_maximum py_compress_decompress py_spiral_matrix
	py_room_scheduler py_graph_cycle_detector py_island_matrix_counter
	py_prism_detector py_word_ladder prefix_dictionary pack_strings task_order
	redundant_link trie_autocomplete union_find_system cache_keeper min_heap
	bridge_finder
	bracket_validator cryptic_sorter echo_validator mirror_matrix
	number_base_converter pattern_tracker anagram shadow_merge
	string_permutation_checker string_sculptor twist_sequence whisper_cipher
	array_rotation_detector constellation_mapper list_intersection_finder
	merge_sorted_lists palindrome_partitioner package_dependency_resolver
	sliding_window_maximum compress decompress generate_spiral island_matrix_counter
	prism_detector word_ladder pack unpack
""".split())

class TestOriginality(unittest.TestCase):
	"""Every variant of every exercise has a name of its own."""

	def test_no_variant_has_the_name_of_a_real_subject(self):
		"""Neither the exercise nor any of its variants, nor its files."""
		catalog = load_catalog()
		for name, exo in catalog.exercises.items():
			self.assertNotIn(name, REAL_SUBJECTS)
			for params in exo.combinations():
				variant = Variant(exo, 0, params)
				with self.subTest(variant=variant.name):
					self.assertNotIn(variant.name, REAL_SUBJECTS)
					for file in variant.expected_files:
						self.assertNotIn(Path(file).stem, REAL_SUBJECTS)
