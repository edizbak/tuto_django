from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..views import BoardListView, TopicListView, new_topic
from ..models import Board, Topic, Post
from ..forms import NewTopicForm

class NewTopicTest(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django Board.')
        User.objects.create_user(username='Bobby', email='fils@pute.xyz', password='prt')
        self.client.login(username='Bobby', password='prt')

    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topics_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_new_topics_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('boards_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        url = reverse('new_topic', kwargs={'pk':1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk':1})
        data = {
            'subject': 'Titre test',
            'message': 'Gnagnanagnagnga gnangna'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_contains_form(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):
        '''
        des donnees invalides ne doivent pas rediriger
        on veut reafficher la page de post avec les erreurs de validation
        '''
        url = reverse('new_topic', kwargs={'pk':1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_empty_fields(self):
        '''
        des donnees invalides ne doivent pas rediriger
        on veut reafficher la page de post avec les erreurs de validation
        '''
        url = reverse('new_topic', kwargs={'pk':1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

class LoginRequiredNewTopicTests(TestCase):
	def setUp(self):
		Board.objects.create(name="Django", description="Foroume de test")
		self.url = reverse('new_topic', kwargs={'pk': 1})
		self.response = self.client.get(self.url)

	def test_redirection(self):
		login_url = reverse('login')
		self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))