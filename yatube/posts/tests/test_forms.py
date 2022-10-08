import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='user_author'
        )
        cls.commentator = User.objects.create_user(
            username='commentator'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',

        )
        cls.post = Post.objects.create(
            text='Текст поста созданого в фикстурах',
            author=cls.user_author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_post_create_unauthorized_user(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост, созданный не авторизированным клиентом. ',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        redirect = f"{reverse('login')}?next={reverse('posts:post_create')}"
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_create_authorized_user(self):
        """Проверка создания записи авторизированным клиентом."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый пост, созданный авторизированным клиентом.',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user_author.username])
        )
        new_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.image.name, f"posts/{form_data['image']}")

    def test_post_edit_unauthorized_user(self):
        """Проверка редактирования записи не авторизированным клиентом."""
        form_data = {
            'text': 'Текст поста ,измененный не авторизированным клиентом.',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        redirect = (reverse('login') + '?next=' + reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, redirect)
        not_edit_post = Post.objects.first()
        self.assertEqual(not_edit_post.id, self.post.id)
        self.assertNotEqual(not_edit_post.text, form_data['text'])
        self.assertEqual(not_edit_post.text, self.post.text)

    def test_post_edit_authorized_user(self):
        """Проверка редактирования записи авторизированным клиентом."""
        form_data = {
            'text': 'Текст поста ,измененный авторизированным клиентом.',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=self.group.id,
            author=self.user_author).exists()
        )

    def test_post_add_comment_authorized_user(self):
        """Проверка создания коментария авторизированным клиентом."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Коментарий от авторизированного пользователя'}
        self.authorized_client.force_login(self.commentator)
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'],
            post_id=self.post.id,
            author=self.commentator,
        ).exists()
        )

    def test_post_add_comment_unauthorized_user(self):
        """Проверка создания коментария не авторизированным клиентом."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Коментарий от не авторизированного пользователя'}
        response = self.guest_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        redirect = (reverse('login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, redirect)
        self.assertEqual(Comment.objects.count(), comments_count)
