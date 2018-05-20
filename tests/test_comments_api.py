import unittest

from stackexchangepy.client import ExchangeClient
import time
import datetime as dt
import os

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
KEY = os.getenv('KEY')

class TestCommentsAPI(unittest.TestCase):
	
	def setUp(self):
		self.client = ExchangeClient(access_token=ACCESS_TOKEN, key=KEY)

	def test_get_comments(self):

		comments = self.client \
					.comments(). \
					get()

		print(type(comments))
		print(dir(comments))
		self.assertTrue(len(comments) > 0)

	def test_add_a_flag(self):

		time.sleep(2)
		client = ExchangeClient(access_token=ACCESS_TOKEN, key=KEY)
		comment = client. \
					comments(7886). \
					option_id(46534). \
					flags(). \
					add(preview=True)

		print(comment)
		self.assertTrue(len(comment) > 0)