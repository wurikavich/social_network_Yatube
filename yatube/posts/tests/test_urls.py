from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='user_author'
        )
        cls.user_another = User.objects.create_user(
            username='user_another'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текст который больше 15 символов',
            author=cls.user_author,
            group=cls.group,
        )
        cls.follow = Follow.objects.create(
            user=cls.user_author,
            author=cls.user_another,
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_author)
        cache.clear()

    def test_url_correct_reverse_name(self):
        """Проверка, что URL-адрес соответвсует reverse('app_name:name')."""
        templates_pages_names = {
            '/': reverse('posts:index'),
            f'/group/{self.group.slug}/': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            f'/profile/{self.user_author.username}/': reverse(
                'posts:profile', args=[self.user_author.username]),
            f'/posts/{self.post.id}/': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}),
            f'/posts/{self.post.id}/edit/': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}),
            '/create/': reverse('posts:post_create'),
            f'/posts/{self.post.id}/comment/': reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}),
            '/follow/': reverse('posts:follow_index'),
            f'/profile/{self.user_author.username}/follow/': reverse(
                'posts:profile_follow', args=[self.user_author.username]),
            f'/profile/{self.user_author.username}/unfollow/': reverse(
                'posts:profile_unfollow', args=[self.user_author.username]),
        }
        for url, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(url, reverse_name)

    def test_url_reverse_uses_correct_template(self):
        """Проверка, что URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user_author.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_user_status_code_bool(self):
        """Проверка доступа для пользователей."""
        field_urls_code = (
            (reverse('posts:index'), HTTPStatus.OK, None),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             HTTPStatus.OK, None),
            (reverse('posts:group_list', kwargs={'slug': 'bad_slug'}),
             HTTPStatus.NOT_FOUND, None),
            (reverse('posts:group_list', kwargs={'slug': 'bad_slug'}),
             HTTPStatus.NOT_FOUND, True),
            (reverse('posts:profile', args=[self.user_author.username]),
             HTTPStatus.OK, None),
            (reverse('posts:profile', kwargs={'username': 'bad_username'}),
             HTTPStatus.NOT_FOUND, None),
            (reverse('posts:profile', kwargs={'username': 'bad_username'}),
             HTTPStatus.NOT_FOUND, True),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             HTTPStatus.OK, None),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             HTTPStatus.FOUND, None),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
             HTTPStatus.OK, True),
            (reverse('posts:post_create'), HTTPStatus.FOUND, None),
            (reverse('posts:post_create'), HTTPStatus.OK, True),
            (reverse('posts:add_comment', kwargs={
                'post_id': self.post.id}), HTTPStatus.FOUND, None),
            (reverse('posts:add_comment', kwargs={
                'post_id': self.post.id}), HTTPStatus.FOUND, True),
            (reverse('posts:follow_index'), HTTPStatus.FOUND, None),
            (reverse('posts:follow_index'), HTTPStatus.OK, True),
            (reverse('posts:profile_follow', args=[self.user_author.username]),
                HTTPStatus.FOUND, None),
            (reverse('posts:profile_follow', args=[self.user_author.username]),
                HTTPStatus.FOUND, True),
            (reverse('posts:profile_unfollow', args=[
                self.user_another.username]), HTTPStatus.FOUND, True),
            ('/unexisting_page/', HTTPStatus.NOT_FOUND, None),
        )
        for url, response_code, args in field_urls_code:
            with self.subTest(url=url):
                status_code = self.unauthorized_user.get(url).status_code
                if args:
                    status_code = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_unauthorized_user_redirect_status_code(self):
        """Проверка редиректа для неавторизованного пользователя."""
        field_urls_code = (
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            reverse('posts:post_create'),
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            reverse('posts:follow_index'),
            reverse('posts:profile_follow', args=[self.user_author.username]),
        )
        for url in field_urls_code:
            with self.subTest(url=url):
                response = self.unauthorized_user.get(url, follow=True)
                redirect = f"{reverse('login')}?next={url}"
                self.assertRedirects(response, redirect)

    def test_authorized_user_redirect_post_edit(self):
        """Проверка редиректа при редактировании автором чужого поста."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_user.force_login(self.user_another)
        response = self.authorized_user.get(url, follow=True)
        redirect = reverse('posts:post_detail', args=[self.post.pk])
        self.assertRedirects(response, redirect)

    def test_authorized_user_redirect_add_comment(self):
        """Проверка редиректа после добавление коментария пользователем."""
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        response = self.authorized_user.get(url, follow=True)
        redirect = reverse('posts:post_detail', args=[self.post.pk])
        self.assertRedirects(response, redirect)

    def test_authorized_user_redirect_add_follow(self):
        """Проверка редиректа после подписки на пользователя."""
        url = reverse('posts:profile_follow', args=[self.user_author.username])
        response = self.authorized_user.get(url, follow=True)
        redirect = reverse('posts:profile', args=[self.user_author.username])
        self.assertRedirects(response, redirect)

    def test_authorized_user_redirect_unfollow(self):
        """Проверка редиректа после отписки от пользователя."""
        url = reverse('posts:profile_unfollow',
                      args=[self.user_another.username])
        response = self.authorized_user.get(url, follow=True)
        redirect = reverse('posts:profile', args=[self.user_another.username])
        self.assertRedirects(response, redirect)
