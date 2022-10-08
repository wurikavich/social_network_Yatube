from math import ceil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()


class PaginatorCountTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='user_author'
        )
        cls.user_follower = User.objects.create_user(
            username='follower'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.ALL_POST_COUNT = 16

        Post.objects.bulk_create(
            Post(author=cls.user_author,
                 text=f'Тестовый пост{num_post}',
                 group=cls.group)
            for num_post in range(cls.ALL_POST_COUNT)
        )
        cls.follow = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user_author,
        )

    def setUp(self):
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follower)

    def test_paginator(self):
        """Проверка работы пагинатора"""
        last_page = ceil(self.ALL_POST_COUNT / settings.NUMBER_POST)
        count_posts_on_page = (self.ALL_POST_COUNT - (last_page - 1)
                               * settings.NUMBER_POST)

        url_pages = (
            (reverse('posts:index'), 'posts/index.html', None),
            (reverse('posts:group_list', args=[self.group.slug]),
             'posts/group_list.html', None),
            (reverse('posts:profile', args=[self.user_author.username]),
             'posts/profile.html', None),
            (reverse('posts:follow_index'), 'posts/follow.html', True),
        )
        for reverse_name, template, args in url_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_client.get(
                    reverse_name, {'page': last_page}
                )
                if args:
                    response = self.authorized_client.get(
                        reverse_name, {'page': last_page}
                    )
                self.assertEqual(
                    len(response.context['page_obj']), count_posts_on_page
                )
                response = self.unauthorized_client.get(reverse_name)
                if args:
                    response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), settings.NUMBER_POST
                )
