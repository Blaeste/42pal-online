"""Tests of pal42.retry: how long to wait after a failed grademe.

Run all the tests from the project root with: python3 -m unittest -v
"""

import unittest

from pal42.retry import RetryPolicy

class TestRetryPolicy(unittest.TestCase):
	"""RetryPolicy(minutes): the wait after the 1st, 2nd... failure."""

	def test_first_failure_is_free_then_the_wait_grows_and_the_last_repeats(self):
		"""0, 5, 10 minutes, then 10 again for every next failure."""
		policy = RetryPolicy((0, 5, 10))
		self.assertEqual(
			[policy.wait_after(failures) for failures in range(1, 6)],
			[0, 300, 600, 600, 600],
		)

	def test_no_failure_means_no_wait(self):
		"""Before any failure, grademe is always possible."""
		self.assertEqual(RetryPolicy((0, 5)).wait_after(0), 0)

	def test_minutes_can_be_halves(self):
		"""42_EXAM waits half a minute after the first failure: 30 seconds."""
		self.assertEqual(RetryPolicy((0.5, 2.5)).wait_after(1), 30)
		self.assertEqual(RetryPolicy((0.5, 2.5)).wait_after(2), 150)
