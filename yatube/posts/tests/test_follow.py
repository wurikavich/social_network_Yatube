from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_post_author = User.objects.create_user(
            username='post_author'
        )
        cls.user_follower = User.objects.create_user(
            username='follower'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текст поста созданого в фикстурах',
            author=cls.user_post_author,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follower)

    def test_subscribe_to_the_author_authorized_user(self):
        """Проверка функции подписаться на автора."""
        subscriptions_count = Follow.objects.count()
        response = self.authorized_client.post(
            reverse('posts:profile_follow',
                    args=[self.user_post_author.username]),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user_post_author.username])
        )
        self.assertEqual(Follow.objects.count(), subscriptions_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.user_follower,
            author=self.user_post_author,
        ).exists()
        )

    def test_unsubscribe_to_the_author_authorized_user(self):
        """Проверка функции отписаться от автора."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_post_author,
        )
        subscriptions_count = Follow.objects.count()
        response = self.authorized_client.post(
            reverse('posts:profile_unfollow',
                    args=[self.user_post_author.username]),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user_post_author.username])
        )
        self.assertEqual(Follow.objects.count(), subscriptions_count - 1)
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower,
            author=self.user_post_author,
        ).exists()
        )

    def test_checking_new_post_signed_user(self):
        """Проверка появления записи у подписаннного пользователя."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_post_author,
        )
        response = self.authorized_client.post(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post, response.context['page_obj'])

    def test_checking_new_post_unsigned_user(self):
        """Проверка появления записи у не подписаннного пользователя."""
        response = self.authorized_client.post(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response.context['page_obj'])
