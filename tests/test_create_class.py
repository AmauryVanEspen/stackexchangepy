import unittest

from stackexchangepy.model import create_class

class TestCreateClass(unittest.TestCase):

	def test_create_class(self):
		newclass = create_class('Test', {
			'same': 'Test',
			'subFields': {
				'name': 'Subfield',
				'name2': 'Another field',
				'subSubField': {
					'name': 'SubSubfield',
				}
			}
		})

		self.assertTrue(hasattr(newclass.subFields, 'subSubField'))