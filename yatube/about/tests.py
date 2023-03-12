from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    page_data = {
        'author': ('/about/author/', 'about/author.html'),
        'tech': ('/about/tech/', 'about/tech.html'),
    }

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/<slug>/."""
        for value, expected in self.page_data.items():
            with self.subTest(value=value):
                response = self.guest_client.get(expected[0])
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /about/<slug>/."""
        for value, expected in self.page_data.items():
            with self.subTest(value=value):
                response = self.guest_client.get(expected[0])
                self.assertTemplateUsed(response, expected[1])
