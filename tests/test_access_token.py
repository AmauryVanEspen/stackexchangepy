import unittest
import os

from stackexchangepy.client import ExchangeClient

class TestAccessToken(unittest.TestCase):

	def setUp(self):
		access_token = os.getenv('ACCESS_TOKEN')
		key = os.getenv('KEY')
		self.client = ExchangeClient()

	def test_invalidate_access_token(self):
		token = 'ti5aUPRVvLyTTxYwnZfQig))'

		response = self.client. \
						access_tokens(123456). \
						invalidate()

		print(response)

		self.assertTrue(len(response) > 0)