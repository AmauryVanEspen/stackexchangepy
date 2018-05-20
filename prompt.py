import requests
import getpass


"""
Simple prompt script for obtaining an access token.
"""

import re

from stackexchangepy.oauth2 import ExchangeAuth

auth = ExchangeAuth()

CLIENT_ID = input("Client ID: ").strip()
CLIENT_SECRET = input("Client secret: ").strip()
REDIRECT_URI = input("Redirect URI(required): ").strip()
SCOPE = input("Colon delimetted scopes: ").strip()
STATE = input("State: ").strip()


while not REDIRECT_URI:
	REDIRECT_URI = input("Redirect URI must be provided: ").strip()

url = auth.authorization_url(client_id=CLIENT_ID, state=STATE, redirect_uri=REDIRECT_URI, scope=[scope for scope in SCOPE.split(",")])

print("Visit: {}".format(url))
response_url = input("Copy redirect url: ").strip()
access_token = auth.access_token(url=response_url, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

print("\nYour access_token is: {}\n".format(access_token['access_token']))
