import unittest
from random import randint
import re

import datetime as dt

import requests

from stackexchangepy.model import create_class
from stackexchangepy.exception import ExchangeException
from stackexchangepy.sites import *

class FakeClient(object):
	BASE_URL = 'https://api.stackexchange.com'
	post_methods = ['add', 'accept', 'edit', 'create', 'undo', 'render', 'delete', 'favorite', 'upvote', 'downvote', 'invalidate', 'de_authenticate', 'get']
	query_params = ['accepted', 'body', 'closed', 'comment', 'filter', 'fromdate', 'inname', 'intitle', 'max', 'migrated', 'min', 
					'notice', 'nottagged','option_id',  'order', 'page', 'pagesize', 'preview', 'q', 'question_id', 'since',
					'sort', 'tagged', 'target_site', 'title', 'todate', 
					'url', 'user', 'views', 'wiki']

	exclude_fields = ['option_id', 'question_id', 'target_site', 'all_time']
	network_methods = ["access-tokens/.*", "apps/.*", "filters.*", 'errors/.*', 'sites', '(users/.*|me)/associated', '(users/.*|me)/merges', '(2\.2/|2\.1/|2\.0/)inbox(/unread)?']

	def __init__(self, version=2.2, access_token=None, key=None, site=Site.STACKOVERFLOW):
		self._version 	= str(version)
		self._token 	= access_token
		self._key 		= key
		self._params 	= {'site': site}
		self._url 		= "{}/{}".format(self.BASE_URL, version)

	def __str__(self):
		return "{} {} {}".format("StackExchange API", self._version, self._site)

	def __getattr__(self, name):
		def _set(*args, **kwargs):
			args = list(args)
			_name = name.replace('_', '-') if re.match(r".*_.*", name) and not name in self.exclude_fields else name
			if name in self.post_methods:
				self._url += "/{}".format(_name) if name in self.post_methods[:-1] else ""
				params = self._form_params()

				self._url += "/undo" if 'undo' in kwargs else ""
				if 'preview' in kwargs:
					params['preview'] = 'true'

				return { 'url': self._url, 'params': params }
			else:
				#_name = name.replace('_', '-') if re.match(r".*_.*", name) and not name in self.exclude_fields else name
				if re.match(r".*search.*", self._url) and _name == 'answers' or \
					re.match(r".*questions.*", self._url) and _name == "tags" or \
					_name in self.query_params:
					self._params[_name] = self._unix_time(args[0]) if type(args[0]) == dt.datetime  \
						else ";".join(map(lambda _id: str(_id).lower() if not type(_id) == str else _id, args))
				else:
					self._item = _name
					_args = "/" + ";".join(map(lambda _id: str(_id), args)) if args else ""
					self._url += "/{}{}".format(_name, _args)

					for key, value in kwargs.items():
						self._params[key] = ";".join(value) if not type(value) == bool else value

			return self
		return _set


	def _form_params(self):
		params = {}

		if self._token:
			params['access_token'] = self._token

		if self._key:
			params['key'] = self._key

		params.update({ key: value for key, value in self._params.items() })

		v = "".format(self.version).replace(".", "\.")

		if any([rg for rg in self.network_methods if re.findall(r"{}".format(rg), self._url)]):
			params.pop('site')

		return params

	def _unix_time(self, date):
		time = dt.time(0, 0, 0)
		datetime = dt.datetime.combine(date, time)
		return datetime.strftime('%s')


class TestURL(unittest.TestCase):

	def setUp(self):
		self.fake_access_token = 'Fake Access Token'
		self.fake_key = 'Fake Key'
		self.site = Site.STACKOVERFLOW
		self.client = FakeClient(access_token=self.fake_access_token, key=self.fake_key, site=self.site)

	def test_answers_url(self):
		answers = self.client.answers().get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(answers, expected)

	def test_answers_ids_url(self):
		fake_ids = []
		for i in range(1, 10):
			fake_ids.append(randint(1212212, 124345656))

		answers = self.client.answers(*fake_ids).get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(answers, expected)


	def test_answers_accept(self):
		fake_id = randint(534321, 121243554)
		answer = self.client.answers(fake_id).accept()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}/accept'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}
		self.assertEqual(answer, expected)

	def test_answers_accept_with_preview(self):
		fake_id = randint(534321, 121243554)
		answer = self.client.answers(fake_id).accept(preview=True)

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}/accept'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'preview': 'true' }
		}
		self.assertEqual(answer, expected)


	def test_answers_accept_undo(self):
		fake_id = randint(534321, 121243554)
		answer = self.client.answers(fake_id).accept(undo=True)

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}/accept/undo'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(answer, expected)

	def test_answers_ids_random_queries(self):
		fake_ids = []
		for i in range(1, 10):
			fake_ids.append(randint(1212212, 124345656))

		answers = self.client \
					.answers(*fake_ids) \
					.filter('witbody') \
					.page(1) \
					.pagesize(100) \
					.fromdate(dt.datetime(2011, 11, 11)) \
					.get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 
						'key': self.fake_key, 
						'site': self.site,
						'filter': 'witbody',
						'pagesize': '100',
						'page': '1',
						'fromdate': '1320962400' }
		}

		self.assertEqual(expected, answers)


	def test_answers_ids_downvote(self):
		fake_id = randint(534321, 121243554)
		answer = self.client.answers(fake_id).downvote()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}/downvote'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(answer, expected)

	def test_answers_ids_downvote_undo(self):
		fake_id = randint(534321, 121243554)
		answer = self.client.answers(fake_id).downvote(undo=True)

		expected = {
			'url': 'https://api.stackexchange.com/2.2/answers/{}/downvote/undo'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(answer, expected)

	def test_badges(self):

		badges = self.client. \
						badges(). \
						page(10). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/badges',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site, 'page': str(10) }
		}

		self.assertEqual(badges, expected)

	def test_badges_ids(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(23212, 11237428))

		badges = self.client.badges(*fake_ids).get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/badges/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(badges, expected)

	def test_badges_name(self):
		
		badges = self.client. \
						badges(). \
						name().	\
						sort('rank'). \
						page(10). \
						inname('rank'). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/badges/name',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'sort': 'rank', 'page': str(10), 'inname': 'rank' }
		}

		self.assertEqual(badges, expected)

	def test_badges_recipients(self):
		badges = self.client. \
						badges(). \
						recipients(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/badges/recipients',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(badges, expected)

	def test_badges_recipients_ids(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(23212, 11237428))

		badges = self.client. \
						badges(*fake_ids). \
						recipients(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/badges/{}/recipients'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(badges, expected)

	def test_badges_tags(self):
		badges = self.client. \
					badges(). \
					tags(). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/badges/tags',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(badges, expected)

	def test_comments(self):

		comments = self.client. \
						page(1). \
						pagesize(100). \
						comments(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'page': str(1), 'pagesize': str(100) }
		}

		self.assertEqual(comments, expected)

	def test_comments_ids(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))

		comments = self.client. \
						order('asc'). \
						sort('votes'). \
						comments(*fake_ids). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'sort': 'votes', 'order': 'asc' }
		}

		self.assertEqual(comments, expected)

	def test_comments_delete(self):

		comment = self.client. \
						comments(231211). \
						delete()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments/231211/delete',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(comment, expected)

	def test_comment_edit(self):

		comment = self.client. \
						comments(232323). \
						body("Some text"). \
						edit()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments/232323/edit',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'body': 'Some text' }
		}

		self.assertEqual(comment, expected)

	def test_comments_flags_add(self):
		rand_id = randint(12122, 12121393)
		rand_option_id = randint(121212, 1212122121212)

		comment = self.client. \
						comments(rand_id). \
						flags(). \
						option_id(rand_option_id). \
						add()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments/{}/flags/add'.format(rand_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'option_id': str(rand_option_id) }
		}

		self.assertEqual(comment, expected)


	def test_comments_flags_options(self):
		fake_id = randint(12121, 1212212)
		options = self.client. \
						comments(fake_id). \
						flags(). \
						options(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments/{}/flags/options'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(options, expected)

	def test_comments_upvote(self):
		fake_id = randint(131212, 13121221222)
		comment = self.client. \
						comments(fake_id). \
						upvote(undo=True, preview=True)

		expected = {
			'url': 'https://api.stackexchange.com/2.2/comments/{}/upvote/undo'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'preview': 'true' }
		}
		self.assertEqual(comment, expected)

	def test_events(self):

		events = self.client. \
						events(). \
						since(dt.datetime.today()). \
						get()


		expected = {
			'url': 'https://api.stackexchange.com/2.2/events',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'since':  FakeClient()._unix_time(dt.datetime.today())}
		}

		self.assertEqual(events, expected)

	def test_info(self):
		info = self.client \
					.info(). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/info',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(info, expected)

	def test_posts(self):

		posts = self.client. \
					posts(). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(posts, expected)

	def test_posts_ids(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))

		posts = self.client. \
						posts(*fake_ids). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(posts, expected)

	def test_posts_ids_comments(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))

		posts = self.client. \
						posts(*fake_ids). \
						comments(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts/{}/comments'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(posts, expected)

	def test_posts_ids_comments_add(self):
		fake_id = randint(321222, 2323282712)

		posts = self.client. \
						posts(fake_id). \
						comments(). \
						body("Some body"). \
						add()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts/{}/comments/add'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'body': 'Some body' }
		}

		self.assertEqual(posts, expected)

	def test_posts_id_comments_render(self):
		fake_id = randint(321222, 2323282712)

		posts = self.client. \
						posts(fake_id). \
						comments(). \
						body("Some body"). \
						render()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts/{}/comments/render'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'body': 'Some body' }
		}

		self.assertEqual(posts, expected)

	def test_posts_ids_revision(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))


		posts = self.client. \
						posts(*fake_ids). \
						revisions(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts/{}/revisions'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(posts, expected)

	def test_posts_ids_suggested_edits(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))

		posts = self.client. \
						posts(*fake_ids). \
						suggested_edits(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/posts/{}/suggested-edits'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(posts, expected)

	def test_privileges(self):
		privileges = self.client. \
						privileges(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/privileges',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(privileges, expected)

	def test_questions(self):
		questions = self.client. \
						questions(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(questions, expected)

	def test_questions_ids(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))
		
		questions = self.client. \
						questions(*fake_ids). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_ids_answers(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))
		
		questions = self.client. \
						questions(*fake_ids). \
						answers(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/answers'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_id_answer_add(self):
		fake_id = randint(1212323, 112121221212)

		question = self.client. \
						questions(fake_id). \
						answers(). \
						body('Some body'). \
						add()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/answers/add'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
			'body': 'Some body' }
		}

		self.assertEqual(question, expected)

	def test_questions_id_answers_render(self):
		fake_id = randint(1212323, 112121221212)

		question = self.client. \
						questions(fake_id). \
						answers(). \
						render()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/answers/render'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(question, expected)

	def test_questions_id_close_options(self):
		fake_id = randint(1212323, 112121221212)

		question = self.client. \
						questions(fake_id). \
						close(). \
						options(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/close/options'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(question, expected)

	def test_questions_comments(self):
		fake_ids = []
		for i in range(0, 10):
			fake_ids.append(randint(321222, 2323282712))
		
		questions = self.client. \
						questions(*fake_ids). \
						comments(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/comments'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_delete(self):
		fake_id = randint(11313, 12121212)

		question = self.client. \
					questions(fake_id). \
					delete()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/delete'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(question, expected)


	def test_questions_downvote(self):
		fake_id = randint(11313, 12121212)

		question = self.client. \
					questions(fake_id). \
					downvote()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/downvote'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(question, expected)

	def test_question_edit(self):
		fake_id = randint(11313, 12121212)

		question = self.client. \
					questions(fake_id). \
					title("Title"). \
					body("Body"). \
					tags('tag1', 'tag2', 'tag3'). \
					comment('Comment'). \
					edit()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/edit'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'title': 'Title', 'body': 'Body', 'tags': "tag1;tag2;tag3", 'comment': "Comment" }
		}		

		self.assertEqual(question, expected)


	def test_question_favorite(self):
		fake_id = randint(12121, 1212121212)

		question = self.client. \
						questions(fake_id). \
						favorite()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/favorite'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(question, expected)

	def test_questions_flags_add(self):
		fake_id = randint(12121, 1212121212)
		fake_option = randint(12121, 354322112)

		question = self.client. \
						questions(fake_id). \
						flags(). \
						option_id(fake_option). \
						target_site('site'). \
						question_id(fake_id). \
						add()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/flags/add'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'option_id': str(fake_option), 'question_id': str(fake_id), 'target_site': 'site' }
		}		

		self.assertEqual(question, expected)

	def test_questions_flags_options(self):
		fake_id = randint(1212, 122122)

		questions = self.client. \
						questions(fake_id). \
						flags(). \
						options(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/flags/options'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_linked(self):
		fake_id = randint(1212, 122122)

		questions = self.client. \
						questions(fake_id). \
						linked(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/linked'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_related(self):
		fake_id = randint(1212, 122122)

		questions = self.client. \
						questions(fake_id). \
						related(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/related'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_timeline(self):
		fake_id = randint(1212, 122122)

		questions = self.client. \
						questions(fake_id). \
						timeline(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/timeline'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_upvote(self):
		fake_id = randint(1212, 122122)

		questions = self.client. \
						questions(fake_id). \
						upvote()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/{}/upvote'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}		

		self.assertEqual(questions, expected)

	def test_questions_add(self):

		question = self.client. \
					questions(). \
					title('Title'). \
					body('Body'). \
					tags('Tag1', 'Tag2'). \
					add()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/add',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
					'title': 'Title', 'body': 'Body', 'tags': "Tag1;Tag2" }
		}

		self.assertEqual(question, expected)

	def test_questions_featured(self):
		question = self.client. \
					questions(). \
					featured(). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/featured',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(question, expected)

	def test_questions_no_answers(self):
		question = self.client. \
					questions(). \
					no_answers(). \
					tagged("Tag1", "Tag2"). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/no-answers',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						"tagged": "Tag1;Tag2" }
		}

		self.assertEqual(question, expected)

	def test_questions_render(self):

		questions = self.client. \
						questions(). \
						tags('tag1', 'tag2'). \
						render()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/render',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						"tags": "tag1;tag2" }
		}

		self.assertEqual(questions, expected)

	def test_questions_unanswered(self):
		questions = self.client. \
						questions(). \
						tagged('tag1', 'tag2'). \
						unanswered(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/unanswered',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						"tagged": "tag1;tag2" }
		}

		self.assertEqual(questions, expected)

	def test_questions_unanswered_my_tags(self):
		questions = self.client. \
						questions(). \
						tagged('tag1', 'tag2'). \
						unanswered(). \
						my_tags(). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/questions/unanswered/my-tags',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						"tagged": "tag1;tag2" }
		}

		self.assertEqual(questions, expected)

	def test_revisions(self):
		fake_id = randint(12112, 3245565)
		revisions = self.client. \
						revisions(fake_id). \
						get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/revisions/{}'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(revisions, expected)

	def test_search(self):
		result = self.client. \
					search(). \
					tagged('tag1', 'tag2'). \
					nottagged('tag3', 'tag4'). \
					intitle('title1'). \
					get()


		expected = {
			'url': 'https://api.stackexchange.com/2.2/search',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
				'intitle': 'title1', 'tagged': 'tag1;tag2', 'nottagged': 'tag3;tag4' }
		}

		self.assertEqual(result, expected)

	def test_search_advanced(self):
		fake_id = randint(2121, 545656)
		views = randint(1221, 12121212)
		result = self.client. \
				search(). \
				advanced(). \
				accepted(True). \
				answers(fake_id). \
				closed(True). \
				migrated(False). \
				notice(True). \
				views(views). \
				wiki(False). \
				url('www'). \
				q('some q'). \
				body('some body'). \
				get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/search/advanced',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
				'accepted': 'true', 'answers': str(fake_id), 'closed': 'true', 'migrated': 'false',
				'notice': 'true', 'views': str(views), 'wiki': 'false', 'url': 'www', 'body': 'some body', 
				'q': 'some q' }
		}

		self.assertEqual(result, expected)


	def test_similar(self):

		result = self.client. \
					similar(). \
					tagged('tag1', 'tag2', 'tag3'). \
					nottagged('tag1', 'tag2'). \
					title('Title'). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/similar',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
				'title': 'Title', 'tagged': 'tag1;tag2;tag3', 'nottagged': 'tag1;tag2' }
		}

		self.assertEqual(result, expected)

	def test_search_excepts(self):
		fake_id = randint(2121, 545656)
		views = randint(1221, 12121212)

		result = self.client. \
					search(). \
					excepts(). \
					accepted(True). \
					answers(fake_id). \
					closed(True). \
					migrated(False). \
					notice(True). \
					views(views). \
					wiki(False). \
					url('www'). \
					q('some q'). \
					body('some body'). \
					user('User'). \
					get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/search/excepts',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
				'accepted': 'true', 'answers': str(fake_id), 'closed': 'true', 'migrated': 'false',
				'notice': 'true', 'views': str(views), 'wiki': 'false', 'url': 'www', 'body': 'some body', 
				'q': 'some q', 'user': 'User' }
		}

		self.assertEqual(result, expected)

	def test_suggested_edits(self):

		edits = self.client. \
				suggested_edits(). \
				sort('creation'). \
				get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/suggested-edits',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
				'sort': 'creation' }
		}

		self.assertEqual(edits, expected)

	def test_suggested_edits_ids(self):

		fake_ids = []
		for i in range(1, 10):
			fake_ids.append(randint(1212212, 124345656))

		edits = self.client. \
				suggested_edits(*fake_ids). \
				sort('creation'). \
				get()

		expected = {
			'url': 'https://api.stackexchange.com/2.2/suggested-edits/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
				'sort': 'creation' }
		}

		self.assertEqual(edits, expected)

	def test_tags(self):

		tags = self.client. \
					tags(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_info(self):

		fake_tags = ["tag1", "tag2", "tag3"]
		tags = self.client. \
					tags(*fake_tags). \
					info(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/info'.format(";".join(fake_tags)),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_moderator(self):

		tags = self.client. \
					tags(). \
					moderator_only(). \
					inname('name'). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/moderator-only',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site,
						'inname': 'name' }
		}

		self.assertEqual(tags, expected)


	def test_tags_required(self):

		tags = self.client. \
					tags(). \
					required(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/required',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_synonyms(self):
		tags = self.client. \
					tags(). \
					synonyms(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/synonyms',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_faqs(self):

		fake_tags = ['tag1', 'tag2', 'tag3']
		tags = self.client. \
					tags(*fake_tags). \
					faq(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/faq'.format(";".join(fake_tags)),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_related(self):
		fake_tags = ['tag1', 'tag2', 'tag3']
		tags = self.client. \
					tags(*fake_tags). \
					related(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/related'.format(";".join(fake_tags)),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_tags_synonyms(self):
		fake_tags = ['tag1', 'tag2', 'tag3']
		tags = self.client. \
					tags(*fake_tags). \
					synonyms(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/synonyms'.format(";".join(fake_tags)),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_top_answers(self):

		tags = self.client. \
				tags('tag1'). \
				top_answers('all_time'). \
				get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/top-answers/{}'.format('tag1', 'all_time'),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_top_askers(self):

		tags = self.client. \
				tags('tag1'). \
				top_askers('all_time'). \
				get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/top-askers/{}'.format('tag1', 'all_time'),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_tags_wikis(self):
		tags = self.client. \
				tags('tag1'). \
				wikis(). \
				get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/tags/{}/wikis'.format('tag1'),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(tags, expected)

	def test_users(self):

		users = self.client. \
					users(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(users, expected)

	def test_users_ids(self):
		fake_ids = [randint(1, 10) for _ in range(1, 10)]
		users = self.client. \
					users(*fake_ids). \
					get()


		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(users, expected)

	def test_me(self):
		me = self.client. \
				me(). \
				get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/me',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(me, expected)

	def test_users_answers(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		users = self.client. \
					users(*fake_ids). \
					answers(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/answers'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(users, expected)

	def test_me_answers(self):
		me = self.client. \
				me(). \
				answers(). \
				get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/me/answers',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(me, expected)

	def test_users_badges(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		badges = self.client. \
					users(*fake_ids). \
					badges(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/badges'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(badges, expected)

	def test_users_comments(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		comments = self.client. \
					users(*fake_ids). \
					comments(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/comments'.format(";".join(map(lambda _id: str(_id), fake_ids))),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(comments, expected)

	def test_users_comments_ids(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		comments = self.client. \
					users(*fake_ids). \
					comments(*fake_ids). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/comments/{}'.format(ids, ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(comments, expected)


	def test_users_favorites(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		favorites = self.client. \
					users(*fake_ids). \
					favorites(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/favorites'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(favorites, expected)

	def test_users_mentioned(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		mentions = self.client. \
					users(*fake_ids). \
					mentioned(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/mentioned'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, mentions)

	def test_users_network_activity(self):
		fake_id = randint(1, 100)
		activity = self.client. \
					users(fake_id). \
					network_activity(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/network-activity'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(activity, expected)

	def test_users_notifications(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		notifications = self.client. \
					users(*fake_ids). \
					notifications(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/notifications'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, notifications)

	def test_users_posts(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		posts = self.client. \
					users(*fake_ids). \
					posts(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/posts'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, posts)

	def test_users_privileges(self):
		fake_id = randint(1, 100)
		user = self.client. \
					users(fake_id). \
					privileges(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/privileges'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, user)

	def test_users_questions(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		questions = self.client. \
					users(*fake_ids). \
					questions(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/questions'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_questions_featured(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		questions = self.client. \
					users(*fake_ids). \
					questions(). \
					featured(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/questions/featured'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_questions_no_answers(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		questions = self.client. \
					users(*fake_ids). \
					questions(). \
					no_answers(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/questions/no-answers'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_unaccepted(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		questions = self.client. \
					users(*fake_ids). \
					questions(). \
					unaccepted(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/questions/unaccepted'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_unanswered(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		questions = self.client. \
					users(*fake_ids). \
					questions(). \
					unanswered(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/questions/unanswered'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_unanswered(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		questions = self.client. \
					users(*fake_ids). \
					reputation(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/reputation'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_reputation_history(self):
		fake_ids = [randint(1, 100) for _ in range(1, 10)]
		history = self.client. \
					users(*fake_ids). \
					reputation_history(). \
					get()

		ids = ";".join(map(lambda _id: str(_id), fake_ids))
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/reputation-history'.format(ids),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, history)


	def test_users_top_answers_tags(self):
		fake_id = randint(1, 100)
		tags = self.client. \
					users(fake_id). \
					top_answers_tags(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/top-answers-tags'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, tags)

	def test_users_top_question_tags(self):
		fake_id = randint(1, 100)
		tags = self.client. \
					users(fake_id). \
					top_question_tags(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/top-question-tags'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, tags)

	def test_users_top_tags(self):
		fake_id = randint(1, 100)
		tags = self.client. \
					users(fake_id). \
					top_tags(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/top-tags'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, tags)

	def test_users_reputation_history_full(self):
		fake_id = randint(1, 100)
		reputation = self.client. \
					users(fake_id). \
					reputation_history(). \
					full(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/reputation-history/full'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, reputation)

	def test_users_suggested_edits(self):
		fake_id = randint(1, 100)
		edits = self.client. \
					users(fake_id). \
					suggested_edits(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/suggested-edits'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, edits)

	def test_users_tags_top_answers(self):
		fake_id = randint(1, 100)
		answers = self.client. \
					users(fake_id). \
					tags('tag1', 'tag2'). \
					top_answers(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/tags/{}/top-answers'.format(fake_id, ";".join(['tag1', 'tag2'])),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, answers)

	def test_users_tags_top_questions(self):
		fake_id = randint(1, 100)
		questions = self.client. \
					users(fake_id). \
					tags('tag1', 'tag2'). \
					top_questions(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/tags/{}/top-questions'.format(fake_id, ";".join(['tag1', 'tag2'])),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, questions)

	def test_users_moderators(self):
		moderators = self.client. \
					users(). \
					moderators(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/moderators',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, moderators)

	def test_users_moderators_elected(self):
		moderators = self.client. \
					users(). \
					moderators(). \
					elected(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/moderators/elected',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, moderators)

	def test_users_inbox(self):
		fake_id = randint(1, 100)
		inbox = self.client. \
					users(fake_id). \
					inbox(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/inbox'.format(fake_id, ";".join(['tag1', 'tag2'])),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, inbox)

	def test_users_inbox_unread(self):
		fake_id = randint(1, 100)
		inbox = self.client. \
					users(fake_id). \
					inbox(). \
					unread(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/{}/inbox/unread'.format(fake_id),
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 'site': self.site }
		}

		self.assertEqual(expected, inbox)

	def test_filters_create(self):

		filters = self.client. \
						filters(include=["filter"], exclude=["filter"], base=["filter"], unsafe=True). \
						create()
		expected = {
			'url' : 'https://api.stackexchange.com/2.2/filters/create',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 
						'include': 'filter', 'exclude': 'filter', 'base': 'filter','unsafe': True }
		}
		self.assertEqual(filters, expected)


	def test_access_tokens(self): 
		tokens = self.client. \
					access_tokens('token1', 'token2'). \
					invalidate()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/access-tokens/token1;token2/invalidate',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 
			 }
		}

		self.assertEqual(expected, tokens)

	def test_apps_tokens(self):
		tokens = self.client. \
					apps('token1', 'token2'). \
					de_authenticate()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/apps/token1;token2/de-authenticate',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, 
			 }
		}

		self.assertEqual(expected, tokens)

	def test_inbox_site(self):
		inbox = self.client. \
					inbox(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/inbox',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, }
		}

		self.assertEqual(expected, inbox)

	def test_associated_users(self):
		users = self.client. \
					users(1, 2, 3). \
					associated(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/1;2;3/associated',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, }
		}

		self.assertEqual(expected, users)

	def test_user_merges(self):
		users = self.client. \
					users(1, 2, 3). \
					merges(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/users/1;2;3/merges',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, }
		}

		self.assertEqual(expected, users)

	def test_sites(self):
		sites = self.client. \
					sites(). \
					get()

		expected = {
			'url' : 'https://api.stackexchange.com/2.2/sites',
			'params': { 'access_token': self.fake_access_token, 'key': self.fake_key, }
		}

		self.assertEqual(expected, sites)
