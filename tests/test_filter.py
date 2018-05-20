import unittest
from stackexchangepy.client import ExchangeClient

class TestFilter(unittest.TestCase):

	def setUp(self):
		self.client = ExchangeClient()

	def test_create_a_filter(self):

		f = self.client. \
				filters(include=['page'], exclude=['pagesize']). \
				create()

		self.assertTrue('filter' in f[0].__dict__)