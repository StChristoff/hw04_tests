from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.index_url = '/'
        cls.create_url = '/create/'
        cls.follow_index_url = '/follow/'
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
        cls.comment_url = f'/posts/{cls.post.id}/comment/'
        cls.follow_url = f'/profile/{cls.user.username}/follow/'
        cls.unfollow_url = f'/profile/{cls.user.username}/unfollow/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostURLTests.user_2)

    def test_urls_exists_at_desired_location_guest(self):
        """Проверяем доступ к страницам, доступным любому пользователю."""
        response_list = (
            PostURLTests.index_url, PostURLTests.group_url,
            PostURLTests.post_url, PostURLTests.profile_url,
        )
        for slug in response_list:
            with self.subTest(slug=slug):
                response = self.guest_client.get(slug)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_auth(self):
        """Проверяем доступ к страницам, доступным авторизованному
        пользователю."""
        response_list = (
            PostURLTests.create_url,
            PostURLTests.post_edit_url,
        )
        for slug in response_list:
            with self.subTest(slug=slug):
                response = self.authorized_client.get(slug)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Проверяем переадресацию для анонимного пользователя
        с приватных страниц.
        """
        response_list = {
            PostURLTests.create_url:
            '/auth/login/?next=' + PostURLTests.create_url,
            PostURLTests.post_edit_url:
            '/auth/login/?next=' + PostURLTests.post_edit_url,
            PostURLTests.comment_url:
            '/auth/login/?next=' + PostURLTests.comment_url,
            PostURLTests.follow_url:
            '/auth/login/?next=' + PostURLTests.follow_url,
            PostURLTests.unfollow_url:
            '/auth/login/?next=' + PostURLTests.unfollow_url,
            PostURLTests.follow_index_url:
            '/auth/login/?next=' + PostURLTests.follow_index_url,
        }
        for slug, redir_slug in response_list.items():
            with self.subTest(slug=slug):
                response = self.guest_client.get(slug, follow=True)
                self.assertRedirects(response, redir_slug)

    def test_url_redirect_authorized_on_post_detail(self):
        """Проверяем переадресацию для авторизованного пользователя,
        не являющегося автором поста на post_detail"""
        response = self.authorized_client_2.get(
            PostURLTests.post_edit_url, follow=True
        )
        self.assertRedirects(response, PostURLTests.post_url)

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            PostURLTests.index_url: 'posts/index.html',
            PostURLTests.group_url: 'posts/group_list.html',
            PostURLTests.post_url: 'posts/post_detail.html',
            PostURLTests.profile_url: 'posts/profile.html',
            PostURLTests.create_url: 'posts/create_post.html',
            PostURLTests.post_edit_url: 'posts/create_post.html',
            PostURLTests.follow_index_url: 'posts/follow.html',
        }
        for url, template in url_names_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_created_comment_on_post_detail(self):
        """Проверяем переадресацию после создания комментария на post_detail"""
        response = self.authorized_client.get(
            PostURLTests.comment_url, follow=True
        )
        self.assertRedirects(response, PostURLTests.post_url)

    def test_redirect_follow_unfollow_on_post_index(self):
        """Проверяем переадресацию на follow_index после подписки/отписки"""
        request_list = [PostURLTests.follow_url, PostURLTests.unfollow_url,]
        for request in request_list:
            with self.subTest(request=request):
                response = self.authorized_client.get(request, follow=True)
                self.assertRedirects(response, PostURLTests.follow_index_url)
