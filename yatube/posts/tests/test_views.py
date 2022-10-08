import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='user_author'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.image = SimpleUploadedFile(
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
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group,
            image=cls.image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_show_correct_context(self):
        """Проверка,что контекст на страницах правильно сформирован ."""
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(self.post, response.context['page_obj'])
                self.assertEqual(
                    self.post.image, response.context['page_obj'][0].image)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон 'post_detail' сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_form_create_correct_context(self):
        """Шаблон 'form create' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_form_edit_correct_context(self):
        """Шаблон 'form edit' сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['form'].instance, self.post)

    def test_cache(self):
        """Проверка кеширование главной страницы"""
        post_cache = Post.objects.create(
            text='Тест кеша',
            author=self.user,
        )
        post_add = self.authorized_client.get(reverse('posts:index')).content
        post_cache.delete()
        post_delet = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(post_add, post_delet)
        cache.clear()
        post_clear = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(post_add, post_clear)
