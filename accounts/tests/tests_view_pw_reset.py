from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
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


class PasswordResetDoneTests(TestCase):
	def setUp(self):
		url = reverse('password_reset_done')
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/reset/done/')
		self.assertEquals(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase):
	def setUp(self):
		email = 'jeanjean@coin.fr'
		user = User.objects.create_user(username='Jean', email=email, password='1234abcdef')
		
		'''
		on créé un token de réinitialisation valide en se basant sur la méthode utilisée par Django :

		'''
		self.uid = urlsafe_base64_encode(force_bytes(user.pk))
		self.token = default_token_generator.make_token(user)

		url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
		self.response = self.client.get(url, follow=True)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
		self.assertEquals(view.func.view_class, auth_views.PasswordResetConfirmView)
		
	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, SetPasswordForm)

	def test_form_inputs(self):
		'''
		La vue doit contenir deux entrées : csrf et deux champs passsword
		'''
		self.assertContains(self.response, '<input', 3)
		self.assertContains(self.response, 'type="password"', 2)


class InvalidPwResetConfirmTests(TestCase):
	def setUp(self):
		email = 'jeanjean@coin.fr'
		user = User.objects.create_user(username='Jean', email=email, password='1234abcdef')
		uid = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)	

		
		'''
		on invalide le token en changeant le mot de passe
		'''	
		user.set_password('abcdef1234')
		user.save()

		url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
		self.response = self.client.post(url, {'email': 'jeanjean@coin.fr'})

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_html(self):
		pw_reset_url = reverse('password_reset')
		self.assertContains(self.response, 'lien de réinitialisation invalide')
		self.assertContains(self.response, 'href="{0}"'.format(pw_reset_url))


class PasswordResetCompleteTests(TestCase):
	def setUp(self):
		url = reverse('password_reset_complete')
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/reset/complete/')
		self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)