from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse, resolve
from django.test import TestCase

class PwResetTests(TestCase):
	def setUp(self):
		url = reverse('password_reset')
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/reset/')
		self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, PasswordResetForm)

	def test_form_inputs(self):
		'''
		La vue doit contenir deux entrées : csrf et email
		'''
		self.assertContains(self.response, '<input', 2)
		self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPwResetTests(TestCase):
	def setUp(self):
		email = 'jeanmarc@lol.com'
		User.objects.create_user(username='Jean', email=email, password='123abcdef')
		url = reverse('password_reset')
		self.response = self.client.post(url, {'email': email})

	def test_redirection(self):
		'''
		La soumission d'un formulaire valide devrait renvoyer l'utilisateur vers la vue 'password_reset_done'
		'''
		url = reverse('password_reset_done')
		self.assertRedirects(self.response, url)

	def test_send_password_reset_email(self):
		self.assertEqual(1, len(mail.outbox))


class InvalidPwResetTests(TestCase):
	def setUp(self):
		url = reverse('password_reset')
		self.response = self.client.post(url, {'email': 'etnon@kek.net'})

	def test_redirection(self):
		'''
		Même les emails inexistants dans la BD devraient rediriger l'utilisateur
		vers la vue 'password_reset_done'
		'''
		url = reverse('password_reset_done')
		self.assertRedirects(self.response, url)

	def test_no_reset_email_sent(self):
		self.assertEqual(0, len(mail.outbox))