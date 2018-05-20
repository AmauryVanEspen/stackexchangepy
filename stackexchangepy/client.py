import datetime as dt
import re
import os

import requests
from tinynetrc import Netrc

from stackexchangepy.model import create_class
from stackexchangepy.exception import ExchangeException
from stackexchangepy.sites import Site

class ExchangeClient(object):

	BASE_URL = 'https://api.stackexchange.com'
	post_methods = ['add', 'accept', 'edit', 'create', 'undo', 'render', 'delete', 'favorite', 'upvote', 'downvote']
	get_methods = ['de_authenticate', 'invalidate', 'get']

	# params which are not part of the url
	query_params = ['accepted', 'body', 'closed', 'comment', 'filter', 'fromdate', 'inname', 'intitle', 'max', 'migrated', 'min', 
					'notice', 'nottagged','option_id',  'order', 'page', 'pagesize', 'preview', 'q', 'question_id', 'since',
					'sort', 'tagged', 'target_site', 'title', 'todate', 
					'url', 'user', 'views', 'wiki']


	# params for which no replace with "-" should happen
	exclude_fields = ['option_id', 'question_id', 'target_site', 'all_time']

	# methods for which site parameter must be excluded
	network_methods = ["access-tokens/.*", "apps/.*", "filters.*", 'errors/.*', 'sites', '(users/.*|me)/associated', '(users/.*|me)/merges', '(2\.2/|2\.1/|2\.0/)inbox(/unread)?']


	def __init__(self, version=2.2, access_token=None, key=None, site=Site.STACKOVERFLOW):
		"""
		Initializes a new client.
		There are 3 possible ways for providing crenedtials, which will be used by the package.
		1. Give them as a parameter, when you initialize the client.
		2. Give them as a enviroment variable.
		3. Give them as a netrc file. In that case, provide address to the machine to be api.stackexchangepy.com,
		with login your access token and password - your key.

		:param version: Version of the API, which will be used. By default is set to the last version, which is 2.2.
		:param access_token: The token obtained from the steps, decribed in the site: 
		:param key: The key provided from the site, when you registered your app.
		:param site: Site to which queries will be send. By default is set to STACKOVERFLOW.
		"""
		self.version 	= version
		self._params 	= {}
		self._site 		= site
		self._url 		= "{}/{}".format(self.BASE_URL, version)

		self._authentication_crenedtials(access_token=access_token, key=key)


	def __str__(self):
		site = self._params['site'] if 'site' in self._params else 'site is not set'
		return "Name: {}\nVersion: {}\nSite: {}\n".format("StackExchange API", self._version, site)

	def __getattr__(self, name):
		"""
		Constructs the query which will be send to the API.
		Check the documentation for more information. https://github.com/monzita/stackxchangepy/wiki

		After successful operation, remaining requests, has_more and max requests which can be used, are kept in variables.
		"""
		def _set(*args, **kwargs):

			args = list(args)
			_name = name.replace('_', '-') if re.match(r".*_.*", name) and not name in self.exclude_fields else name
			if name in self.post_methods or name in self.get_methods:
				self._url += "/{}".format(_name) if name in self.post_methods or name in self.get_methods[:-1] else ""
				params = self._form_params()

				method = "post" if name in self.post_methods else "get"

				response = requests.post(self._url, data=params) if method == "post" else requests.get(self._url, params=params)
				if response.status_code != requests.codes.ok:
					response = response.json()
					self._reset_state()
					raise ExchangeException(response['error_message'], response['error_name'], response['error_id'])
				
				if name == 'delete':
					return response.status_code

				response = response.json()
				items = [create_class(self._item, item) for item in response['items']]

				self._reset_state()

				self.has_more = response['has_more']
				self.quota_remaining = response['quota_remaining']
				self.quota_max = response['quota_max']

				return items
			else:
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
		params['site'] = self._site

		if any([rg for rg in self.network_methods if re.findall(r"{}".format(rg), self._url)]):
			params.pop('site')

		return params


	def _unix_time(self, date):
		time = dt.time(0, 0, 0)
		datetime = dt.datetime.combine(date, time)
		return datetime.strftime('%s')


	def _authentication_crenedtials(self, access_token=None, key=None):
		netrc = Netrc()

		self._token = access_token or os.getenv('ACCESS_TOKEN') or netrc['api.stackexchangepy.com']['login']
		self._key = key or os.getenv('KEY') or netrc['api.stackexchangepy.com']['password']


	def _reset_state(self):
		self._url = "{}/{}".format(self.BASE_URL, self.version)
		self._params = {}
		self._item = ""