from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
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
            author=cls.user_author,
            text='Тестовая пост длинее 15 символов',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_follower,
            text='Тестовый коментарий',
        )
        cls.follow = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user_author,
        )

    def test_str(self):
        """Проверка __str__ у моделей Group, Post, Comment."""
        value__str__ = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title,
            str(self.comment): self.comment.text,
        }
        for value, expected in value__str__.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_verbose_name(self):
        """Проверка verbose_name у моделей Group, Post, Comment, Follow."""
        field_verboses = (
            ('text', 'Текст поста', self.post),
            ('pub_date', 'Дата публикации', self.post),
            ('author', 'Автор', self.post),
            ('group', 'Группа', self.post),
            ('title', 'Название группы', self.group),
            ('slug', 'Уникальный адрес группы', self.group),
            ('description', 'Описание сообщества', self.group),
            ('post', 'Пост', self.comment),
            ('author', 'Автор', self.comment),
            ('text', 'Коментарий', self.comment),
            ('created', 'Дата создания', self.comment),
            ('user', 'Пользователь', self.follow),
            ('author', 'Автор', self.follow),
        )
        for value, expected, args in field_verboses:
            with self.subTest(value=value):
                self.assertEqual(
                    args._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Проверка help_text у моделей Group, Post, Comment."""
        field_help_texts = (
            ('title', 'Укажите название группы', self.group),
            ('slug', 'Выберите из списка или укажите новый адрес', self.group),
            ('description', 'Добавьте описание группы', self.group),
            ('text', 'Добавьте описание поста', self.post),
            ('group', 'Укажите группу в которой опубликуется пост', self.post),
            ('text', 'Введите текст', self.comment),
        )
        for value, expected, args in field_help_texts:
            with self.subTest(value=value):
                self.assertEqual(
                    args._meta.get_field(value).help_text, expected)
