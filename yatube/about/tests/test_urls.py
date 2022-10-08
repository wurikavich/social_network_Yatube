from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.unauthorized_user = Client()

    def test_url_correct_reverse_name(self):
        """Проверка, что URL-адрес соответвсует reverse('app_name:name')."""
        templates_pages_names = {
            '/about/author/': reverse('about:author'),
            '/about/tech/': reverse('about:tech'),
        }
        for url, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(url, reverse_name)

    def test_url_reverse_uses_correct_template(self):
        """Проверка, что URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_user_status_code_bool(self):
        """Проверка доступа для пользователей."""
        field_urls_code = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.unauthorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)
