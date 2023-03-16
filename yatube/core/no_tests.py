# Михаил, не считай, пожалуйста, за ошибку. Этот файл для 6 спринта.
# Просто пока не работает, и я еще не разобрался почему.

from django.test import TestCase

from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Проверяем, что не существующая страница вызывает ошибку 404,
        и вызывается верный шаблон"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
