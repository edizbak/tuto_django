from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

class PasswordResetMailTests(TestCase):
	def setUp(self):
		User.objects.create_user(username='Jean-Paul', email='jeanpaul@lol.fr', password='123abcdef')
		self.response = self.client.post(reverse('password_reset'), { 'email': 'jeanpaul@lol.fr'})
		self.email = mail.outbox[0]

	def test_email_subject(self):
		self.assertEqual('[Fartotum] Réinitialisation du mot de passe', self.email.subject)

	def test_email_body(self):
		context = self.response.context
		token = context.get('token')
		uid = context.get('uid')
		password_reset_token_url = reverse('password_reset_confirm', kwargs={
			'uidb64': uid,
			'token': token
			})
		self.assertIn(password_reset_token_url, self.email.body)
		self.assertIn('Jean-Paul', self.email.body)
		self.assertIn('jeanpaul@lol.fr', self.email.body)

	def test_email_to(self):
		self.assertEqual(['jeanpaul@lol.fr'], self.email.to)