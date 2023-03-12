from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()

INDEX_URL = '/'
CREATE_URL = '/create/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='User2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.profile_url = f'/profile/{cls.user.username}/'
        cls.post_url = f'/posts/{cls.post.id}/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.group_url = f'/group/{cls.group.slug}/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostURLTests.user_2)

    def test_urls_exists_at_desired_location_guest(self):
        """Страницы доступны любому пользователя."""
        response_list = (
            INDEX_URL, PostURLTests.group_url,
            PostURLTests.post_url, PostURLTests.profile_url,
        )
        for slug in response_list:
            with self.subTest(slug=slug):
                response = self.guest_client.get(slug)
                self.assertEqual(response.status_code, 200)

    def test_urls_exists_at_desired_location_auth(self):
        """Страницы доступны авторизованному пользователю."""
        response_list = (CREATE_URL, PostURLTests.post_edit_url)
        for slug in response_list:
            with self.subTest(slug=slug):
                response = self.authorized_client.get(slug)
                self.assertEqual(response.status_code, 200)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Ссылка перенаправит анонимного пользователя
        на страницу логина.
        """
        response_list = {
            CREATE_URL: '/auth/login/?next=' + CREATE_URL,
            PostURLTests.post_edit_url:
            '/auth/login/?next=' + PostURLTests.post_edit_url,
        }
        for slug, redir_slug in response_list.items():
            with self.subTest(slug=slug):
                response = self.guest_client.get(slug, follow=True)
                self.assertRedirects(response, redir_slug)

    def test_url_redirect_authorized_on_post_detail(self):
        """Ссылка перенаправит авторизованного пользователя, не являющегося
         автором поста на post_detail"""
        response = self.authorized_client_2.get(
            PostURLTests.post_edit_url, follow=True
        )
        self.assertRedirects(response, PostURLTests.post_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            INDEX_URL: 'posts/index.html',
            PostURLTests.group_url: 'posts/group_list.html',
            PostURLTests.post_url: 'posts/post_detail.html',
            PostURLTests.profile_url: 'posts/profile.html',
            CREATE_URL: 'posts/create_post.html',
            PostURLTests.post_edit_url: 'posts/create_post.html',
        }
        for url, template in url_names_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
