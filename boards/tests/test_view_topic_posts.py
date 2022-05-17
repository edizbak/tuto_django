from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..views import PostListView
from ..models import Board, Topic, Post

class TopicPostsTests(TestCase):
	def setUp(self):
		board = Board.objects.create(name='Zboub', description='Foroum de test')
		user = User.objects.create_user(username='Jean', email='nobody@here.com', password='azerty1234')
		topic = Topic.objects.create(subject='Hello world', board=board, starter=user)
		Post.objects.create(message='Un texte presque complètement dénué de sens.', topic=topic, created_by=user)
		url = reverse('topic_posts', kwargs={'pk': board.pk, 'topic_pk': topic.pk})
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/boards/1/sujets/1/')
		self.assertEquals(view.func.view_class, PostListView)