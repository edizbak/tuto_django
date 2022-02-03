from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

class PasswordChangeTests(TestCase):
	def setUp(self):
		email = 'jeanmarc@lol.com'
		User.objects.create_user(username='Jean', email=email, password='123abcdef')
		url = reverse('password_change')
		self.client.login(username='Jean', password='123abcdef')
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_url_resolves_change_view(self):
		view = resolve('/settings/password/')
		self.assertEquals(view.func.view_class, auth_views.PasswordChangeView)

	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, PasswordChangeForm)

	def test_form_inputs(self):
		'''
		La vue doit contenir quatre entrées : csrf, ancien mot de passe, nouveau et confirmation
		'''

		self.assertContains(self.response, '<input', 4)
		self.assertContains(self.response, 'type="password"', 3)

class LoginRequiredPasswordChangeTests(TestCase):
	def test_redirection(self):
		url = reverse('password_change')
		login_url = reverse('login')
		response = self.client.get(url)
		self.assertRedirects(response, f'{login_url}?next={url}')


class PasswordChangeTestCase(TestCase):
	'''
	testcase de base pour l'envoi du formulaire
	prend un dict `data` pour POST la vue
	'''

	def setUp(self, data={}):
		self.user = User.objects.create_user(username='Jean', email='jean@marc.fr', password='old_password')
		self.url = reverse('password_change')
		self.client.login(username='Jean', password='old_password')
		self.response = self.client.post(self.url, data)


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
	def setUp(self):
		super().setUp({
			'old_password': 'old_password',
			'new_password1': 'new_password',
			'new_password2': 'new_password',
			})

	def test_redirection(self):
		'''
		La soumission d'un formulaire valide devrait rediriger l'utilisateur
		'''

		self.assertRedirects(self.response, reverse('password_change_done'))

	def test_password_changed(self):
		'''
		refresh de l'instance d'utilisateur de la DB pour avoir le nouveau hash du mdp
		mis à jour par le changement de mdp
		'''

		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('new_password'))

	def test_user_authentification(self):
		'''
		Créé une nouvelle requête vers une page arbritraire
		La réponse résultante devrait maintenant avoir `user` dans le contexte, après une connexion réussie
		'''

		response = self.client.get(reverse('home'))
		user = response.context.get('user')
		self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase):
	def test_status_code(self):
		'''
		Une soumission de formulaire invalide devrait renvoyer vers la même page
		'''

		self.assertEquals(self.response.status_code, 200)

	def test_form_errors(self):
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

	def test_didnt_change_password(self):
		'''
		on refresh l'instance d'user de la DB pour
		être sûr d'avoir des données à jour
		'''

		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('old_password'))