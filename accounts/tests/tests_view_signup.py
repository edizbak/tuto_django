from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.test import TestCase
from django.urls import reverse, resolve
from ..views import signup
from ..forms import SignUpForm

# Create your tests here.
class SignupTest(TestCase):
	def setUp(self):
		url = reverse('signup')
		self.response = self.client.get(url)

	def test_signup_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_signup_url_resolves_signup_view(self):
		view = resolve('/signup/')
		self.assertEquals(view.func, signup)

	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, SignUpForm)


class SuccessfulSignupTest(TestCase):
	def setUp(self):
		url = reverse('signup')
		data = {
			'username': 'bob',
			'email': 'jean@martin.xyz',
			'password1': 'abcdef123456',
			'password2': 'abcdef123456'
		}
		self.response = self.client.post(url, data)
		self.home_url = reverse('home')

	def test_redirection(self):
		'''
		Une soumission de formulaire valide devrait rediriger sur la home
		'''
		self.assertRedirects(self.response, self.home_url)

	def test_user_creation(self):
		self.assertTrue(User.objects.exists())

	def test_user_authentification(self):
		'''
		On fait une requête vers n'importe quelle page
		La réponse devrait avoir un `user` dans le contexte
		après une authentification réussie
		'''
		response = self.client.get(self.home_url)
		user = response.context.get('user')
		self.assertTrue(user.is_authenticated)

class InvalidSignUpTests(TestCase):
	def setUp(self):
		url = reverse('signup')
		self.response = self.client.post(url, {})

	def test_signup_status_code(self):
		'''
		Une soumission de formulaire invalide devrait renvoyer sur la même page
		'''
		self.assertEquals(self.response.status_code, 200)

	def test_form_errors(self):
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

	def test_dont_create_user(self):
		self.assertFalse(User.objects.exists())