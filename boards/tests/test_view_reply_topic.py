from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..views import reply_topic
from ..models import Board, Topic, Post
from ..forms import PostForm

class ReplyTopicTestCast(TestCase):
	'''
	Base test case to be used in all 'reply_topic' view tests
	'''

	def setUp(self):
		self.board = Board.objects.create(name="Djoungo", description="Djoungou bourde.")
		self.username = 'Gérard'
		self.password = '123'
		user = User.objects.create_user(username=self.username, email='gerard@lenorman.fr', password=self.password)
		self.topic = Topic.objects.create(subject='Hello world', board=self.board, starter=user)
		Post.objects.create(message='Un texte presque complètement dénué de sens.', topic=self.topic, created_by=user)
		self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})

class LoginRequiredReplyTopic(ReplyTopicTestCast):
	def test_redirection(self):
		login_url = reverse('login')
		response = self.client.get(self.url)
		self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class ReplyTopicTests(ReplyTopicTestCast):
	def setUp(self):
		super().setUp()
		self.client.login(username=self.username, password=self.password)
		self.response = self.client.get(self.url)

	def test_status_code(self):
		self.assertEquals(200, self.response.status_code)

	def test_view_function(self):
		view = resolve('/boards/{board_id}/sujets/{topic_pk}/reply/'.format(board_id=self.board.pk, topic_pk=self.topic.pk))
		self.assertEquals(view.func, reply_topic)

	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, PostForm)