from django.test import TestCase
from django.test.client import Client


class ViewTest(TestCase):
	
	fixtures = ['test_data.json']
	
	def setUp(self):
		self.client = Client()
		
	def test_register_page(self):
		data = {
			'username': 'test_user',
			'email': 'test_user@example.com',
			'password1': 'pass1234',
			'password2': 'pass1234',
		}
		response = self.client.post('/register/', data)
		self.assertEqual(response.status_code, 302)
		
	def test_note_save(self):
		response = self.client.login(
			username='sysop',
			password ='password'
		)
		self.assertTrue(response)
		data = {
			'note': 'This is a test',
			'title': 'This is a test title',
			#'tags': 'These are test tags'
		}
		response = self.client.post('/save/', data)
		self.assertEqual(response.status_code, 302)
		response = self.client.get('/user/sysop/')
		self.assertTrue('This is a test' in response.content)
		self.assertTrue('This is a test title' in response.content)
		#self.assertTrue('These are test tags' in response.content)