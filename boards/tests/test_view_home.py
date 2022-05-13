from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..views import boards_topics, new_topic, BoardListView
from ..models import Board, Topic, Post

class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django Board.')
        url = reverse('home')
        self.response = self.client.get(url)
        
    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func.view_class, BoardListView)

    def test_home_view_contains_links_to_other_pages(self):
        board_topic_url = reverse('boards_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topic_url))