import unittest
import time
import datetime as dt
import os

from stackexchangepy.client import ExchangeClient


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
KEY = os.getenv('KEY')

class TestAnswersAPI(unittest.TestCase):

	def setUp(self):
		self.client = ExchangeClient(access_token=ACCESS_TOKEN, key=KEY)

	def test_get_answers(self):
		answers = self.client. \
				answers(). \
				get()

		self.assertTrue(len(answers) > 0)

	def test_get_answers_with_body(self):
		answers = self.client. \
					answers(). \
					filter('withbody'). \
					get()

		self.assertTrue(len(answers) > 0 and hasattr(answers[0], 'body'))
	

	def test_get_flag_options(self):
		options = self.client \
					.answers(50212414)	\
					.flags() \
					.options() \
					.get()

		self.assertTrue(len(options) > 0)

	def test_get_answers_from_given_date(self):
		answers = self.client \
					.answers() \
					.fromdate(dt.datetime(2016, 11, 11)) \
					.get()

		self.assertTrue(len(answers) > 0)

	def test_get_comments_comments(self):
		time.sleep(4)
		comments = self.client \
					.answers(9561207, 42668817) \
					.comments() \
					.order('asc') \
					.get()

		self.assertTrue(len(comments) > 0)
