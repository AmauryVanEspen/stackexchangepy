import unittest
import os
import datetime as dt
import time

from stackexchangepy.client import ExchangeClient

class TestQuestions(unittest.TestCase):
	def setUp(self):
		access_token = os.getenv('ACCESS_TOKEN')
		key = os.getenv('KEY')

		self.client = ExchangeClient(access_token=access_token, key=key, site='stackapps.com')

	def test_removing_a_question(self):
		qid = 7886

		response = self.client. \
						questions(qid). \
						delete()

		print(response)
		self.assertEqual(200, response)