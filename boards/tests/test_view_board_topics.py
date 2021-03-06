from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..views import new_topic, TopicListView
from ..models import Board, Topic, Post

class BoardTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django Board.')

    def test_board_topic_view_success_status_code(self):
        url = reverse('boards_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('boards_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_link_back_to_home(self):
        board_topic_url = reverse('boards_topics', kwargs={'pk': 1})
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        homepage_url = reverse('home')

        response = self.client.get(board_topic_url)

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))