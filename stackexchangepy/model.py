
def create_class(name, response):
	klass = type(name, (object,), {})
	for key, value in response.items():
		if type(value) == dict:
			subklass = create_class(key, value)
			setattr(klass, key, subklass)
		else:
			setattr(klass, key, value)
	return klass