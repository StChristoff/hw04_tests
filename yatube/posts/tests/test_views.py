from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            author=cls.user, text='Тестовый пост', group=cls.group,
        )
        cls.NAME_TEMPL = {
            'INDEX': (reverse('posts:index'), 'posts/index.html'),
            'CREATE': (reverse('posts:post_create'), 'posts/create_post.html'),
            'GROUP_LIST': (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': cls.group.slug}
                ),
                'posts/group_list.html',
            ),
            'PROFILE': (
                reverse(
                    'posts:profile',
                    kwargs={'username': cls.user.username}
                ),
                'posts/profile.html',
            ),
            'DETAIL': (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': cls.test_post.id}
                ),
                'posts/post_detail.html',
            ),
            'EDIT': (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': cls.test_post.id}
                ),
                'posts/create_post.html',
            ),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_pages_use_correct_templates(self):
        """Проверяем, что view-функции используют корректные шаблоны."""
        for reverse_name, template in PostsViewsTests.NAME_TEMPL.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверяем формирование домашней страницы."""
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['INDEX'][0]
        )
        self.response_processing_post(response)

    def test_group_list_page_show_correct_context(self):
        """Проверяем формирование страницы постов группы."""
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['GROUP_LIST'][0]
        )
        self.assertEqual(
            response.context['group'],
            PostsViewsTests.group
        )
        self.response_processing_post(response)

    def test_profile_page_show_correct_context(self):
        """Проверяем формирование страницы профиля пользователя."""
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['PROFILE'][0]
        )
        self.assertEqual(response.context['author'], PostsViewsTests.user)
        self.response_processing_post(response)

    def test_post_detail_page_show_correct_context(self):
        """Проверяем формирование страницы поста."""
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['DETAIL'][0]
        )
        self.response_processing_post(response)

    def test_post_create_page_show_correct_context(self):
        """Проверяем формирование страницы создания поста."""
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['CREATE'][0]
        )
        self.response_processing_form(response)

    def test_post_edit_page_show_correct_context(self):
        """Проверяем формирование страницы редактирования поста."""
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['EDIT'][0]
        )
        self.assertTrue(response.context['is_edit'])
        self.response_processing_form(response)

    def test_created_post_show_on_all_pages(self):
        """Проверяем, что при создании поста он появляется
        на всех нужных страницах (главной, группы, в профайле)"""
        url_requests = [
            PostsViewsTests.NAME_TEMPL['INDEX'][0],
            PostsViewsTests.NAME_TEMPL['GROUP_LIST'][0],
            PostsViewsTests.NAME_TEMPL['PROFILE'][0],
        ]
        for request in url_requests:
            response = self.authorized_client.get(request)
            self.assertIn(
                PostsViewsTests.test_post,
                response.context['page_obj']
            )

    def test_post_not_show_on_other_group_page(self):
        """Проверяем, что пост не отображается в чужой группе"""
        group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug-2',
            description='Тестовое описание_2',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': group_2.slug})
        )
        self.assertNotIn(
            PostsViewsTests.test_post,
            response.context['page_obj']
        )

    def test_index_paginator(self):
        """Проверяем разбивку на страницы паджинатором."""
        objs = [
            Post(
                author=PostsViewsTests.user,
                text='Тестовый пост',
                group=PostsViewsTests.group,
            ) for _ in range(settings.POSTS_PER_PAGE)
        ]
        Post.objects.bulk_create(objs)
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['INDEX'][0]
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_PER_PAGE
        )
        response = self.authorized_client.get(
            PostsViewsTests.NAME_TEMPL['INDEX'][0] + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            (Post.objects.count() - settings.POSTS_PER_PAGE)
        )

    def response_processing_post(self, response):
        if 'post' in response:
            post = response.context['post']
            self.assertIsInstance(post, Post)
            self.assertEqual(post, PostsViewsTests.test_post)
        elif 'page_obj' in response:
            post = response.context['page_obj'][0]
            self.assertIsInstance(post, Post)
            self.assertEqual(post.text, PostsViewsTests.test_post.text)
            self.assertEqual(post.group, PostsViewsTests.test_post.group)
            self.assertEqual(post.author, PostsViewsTests.test_post.author)

    def response_processing_form(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_field)
