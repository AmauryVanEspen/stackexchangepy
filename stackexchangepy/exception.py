

class ExchangeException(Exception):

	def __init__(self, message, name, status_code):
		super().__init__(message)
		self.message = message
		self.name = name
		self.status_code = status_code

	def __str__(self):
		return "\nMessage: {}\nName: {}\nCode: {}".format(self.message, self.name, self.status_code)