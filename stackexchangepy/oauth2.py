import re
import os

import requests
from tinynetrc import Netrc

from stackexchangepy.exception import ExchangeException

class ExchangeAuth(object):
	OAUTH_URL = 'https://stackoverflow.com/oauth'
	ACCESS_TOKEN_URL = 'https://stackoverflow.com/oauth/access_token'

	def authorization_url(self, client_id=None, scope=[], redirect_uri=None, state=None):
		"""
		Returns the address from which to get the code, in order to obtain an access token.
		There are 3 possible ways for providing crenedtials, which will be used by the package.
		1. Give them as a parameter, when you initialize the client.
		2. Give them as a enviroment variable.
		3. Give them as a netrc file. In that case, provide address to the machine to be api.stackexchange.com,
		with login your client_id and password - client_secret.

		:param client_id: The CLIENT ID provided from Stackexchange.
		:param scope: List of scopes, with which you want the access token to be grant.
			Scope can be read_inbox, no_expiry, write_access, private_info. For more information, check the official documentation:
			http://api.stackexchange.com/docs/authentication#scope
		:param redirect_uri: The uri which was provided to the Stackexchange in which your app will be redirected, to get the code.
		:param state:
		:exception: If some of the needed information is missing, like client id, redirect uri or client secret, and error will be
		raised.
		"""
		if not redirect_uri:
			raise ExchangeException('Redirect URI must be provided.', 'authentication', 400)

		netrc = Netrc()
		if not client_id:
			client_id = os.getenv('CLIENT_ID') or netrc['api.stackexchange.com']['login']

		if not client_id:
			raise ExchangeException('Client ID must be provided.', 'authentication', 400)

		url = '{}?client_id={}&redirect_uri={}'.format(self.OAUTH_URL, client_id, redirect_uri)

		if scope:
			url += '&scope={}'.format(','.join(scope))

		if state:
			url += '&state={}'.format(state)

		return url


	def access_token(self, url, client_id=None, client_secret=None, redirect_uri=None):
		"""	
		Return an access token, and if provided expire date of the token.
		There are 3 possible ways for providing crenedtials, which will be used by the package.
		1. Give them as a parameter, when you initialize the client.
		2. Give them as a enviroment variable.
		3. Give them as a netrc file. In that case, provide address to the machine to be api.stackexchange.com,
		with login your client_id and password - client_secret.

		:param url: Which was returned from authenticating your app, with the code.
		:param client_id: Client ID which was provided from the api.
		:param client_secret: Client Secret which was provided from the api.
		:param redirect_uri: The redirect uri which was provided in the api.
		"""

		if not redirect_uri:
			raise ExchangeException('Redirect URI must be provided.', 'authentication', 400)

		netrc = Netrc()
		if not client_id:
			client_id = os.getenv('CLIENT_ID') or netrc['api.stackexchange.com']['login']

		if not client_id:
			raise ExchangeException('Client ID must be provided.', 'authentication', 400)


		if not client_secret:
			client_secret = os.getenv('CLIENT_SECRET') or netrc['api.stackexchange.com']['password']

		if not client_secret:
			raise ExchangeException('Client secret must be provided.', 'authentication', 400)

		code = re.match(r".*(code=)(.*)", url)

		if not code:
			raise ExchangeException('Something went wrong. Code is not found.', 'authentication', 404)

		params = {
			'client_id': client_id,
			'client_secret': client_secret,
			'redirect_uri': redirect_uri,
			'code': code.group(2)
		}

		response = requests.post(self.ACCESS_TOKEN_URL, params=params)

		if response.status_code != requests.codes.ok:
			response = response.text
			raise ExchangeException(response['error_message'], response['error_name'], response['error_id'])

		response_info = response.text.split("&")
		access_token = response_info[0].split("=")[1]
		expire = response_info[1].split("=")[1]

		return { 'access_token': access_token, 'expire': expire }

	def access_token_response(self, url, client_id=None, client_secret=None, redirect_uri=None):
		"""
		The access_token method returns only access token, and date on which expires raw.
		If you want the whole response, without breaking it on parts, use that method.
		There are 3 possible ways for providing crenedtials, which will be used by the package.
		1. Give them as a parameter, when you initialize the client.
		2. Give them as a enviroment variable.
		3. Give them as a netrc file. In that case, provide address to the machine to be api.stackexchange.com,
		with login your client_id and password - client_secret.

		:param url: Which was returned from authenticating your app, with the code.
		:param client_id: Client ID which was provided from the api.
		:param client_secret: Client Secret which was provided from the api.
		:param redirect_uri: The redirect uri which was provided in the api.
		"""


		if not redirect_uri:
			raise ExchangeException('Redirect URI must be provided.', 'authentication', 400)

		netrc = Netrc()
		if not client_id:
			client_id = os.getenv('CLIENT_ID') or netrc['api.stackexchange.com']['login']

		if not client_id:
			raise ExchangeException('Client ID must be provided.', 'authentication', 400)


		if not client_secret:
			client_secret = os.getenv('CLIENT_SECRET') or netrc['api.stackexchange.com']['password']

		if not client_secret:
			raise ExchangeException('Client secret must be provided.', 'authentication', 400)

		code = re.match(r".*(code=)(.*)", url)

		if not code:
			raise ExchangeException('Something went wrong. Code is not found.', 'authentication', 404)

		params = {
			'client_id': client_id,
			'client_secret': client_secret,
			'redirect_uri': redirect_uri,
			'code': code.group(2)
		}

		response = requests.post(self.ACCESS_TOKEN_URL, params=params)

		if response.status_code != requests.codes.ok:
			response = response.json()
			raise ExchangeException(response['error_message'], response['error_name'], response['error_id'])

		return response.text