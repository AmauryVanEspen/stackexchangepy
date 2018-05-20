import unittest
import os
import datetime as dt
import time

from stackexchangepy.client import  ExchangeClient


class TestBadges(unittest.TestCase):

	def setUp(self):
		access_token = os.getenv('ACCESS_TOKEN')
		key = os.getenv('KEY')
		self.client = ExchangeClient(access_token=access_token, key=key)

	def test_get_badges(self):
		badges = self.client. \
						badges(). \
						get()

		self.assertTrue(len(badges) > 0)

	def test_get_badges_name(self):
		time.sleep(2)
		badges = self.client. \
						badges(). \
						name(). \
						fromdate(dt.datetime.today()). \
						min('silver'). \
						get()

		self.assertTrue(len(badges) > 0)