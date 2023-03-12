from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
# from .utils import post_response

User = get_user_model()

POSTS_NAMES_TEMPLATES = {
    'INDEX': ('posts:index', 'posts/index.html'),
    'CREATE': ('posts:post_create', 'posts/create_post.html'),
    'GROUP_LIST': ('posts:group_list', 'posts/group_list.html'),
    'PROFILE': ('posts:profile', 'posts/profile.html'),
    'DETAIL': ('posts:post_detail', 'posts/post_detail.html'),
    'EDIT': ('posts:post_edit', 'posts/create_post.html'),
}

POSTS_PER_PAGE = 10
NUM_OF_POSTS = 11


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
        for _ in range(NUM_OF_POSTS):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )
        cls.test_post = Post.objects.get(pk=1)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_pages_use_correct_templates(self):
        """Проверяем, что view-функции используют корректные шаблоны."""
        templates_pages_names = {
            reverse(POSTS_NAMES_TEMPLATES['INDEX'][0]):
            POSTS_NAMES_TEMPLATES['INDEX'][1],
            reverse(POSTS_NAMES_TEMPLATES['CREATE'][0]):
            POSTS_NAMES_TEMPLATES['CREATE'][1],
            reverse(
                POSTS_NAMES_TEMPLATES['GROUP_LIST'][0],
                kwargs={'slug': PostsViewsTests.group.slug}
            ):
            POSTS_NAMES_TEMPLATES['GROUP_LIST'][1],
            reverse(
                POSTS_NAMES_TEMPLATES['PROFILE'][0],
                kwargs={'username': PostsViewsTests.user.username}
            ):
            POSTS_NAMES_TEMPLATES['PROFILE'][1],
            reverse(
                POSTS_NAMES_TEMPLATES['DETAIL'][0],
                kwargs={'post_id': '1'}
            ):
            POSTS_NAMES_TEMPLATES['DETAIL'][1],
            reverse(
                POSTS_NAMES_TEMPLATES['EDIT'][0],
                kwargs={'post_id': '1'}
            ):
            POSTS_NAMES_TEMPLATES['EDIT'][1],
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверяем формирование домашней страницы."""
        response = self.authorized_client.get(
            reverse(POSTS_NAMES_TEMPLATES['INDEX'][0])
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, PostsViewsTests.test_post.text)
        self.assertEqual(post.group, PostsViewsTests.test_post.group)
        self.assertEqual(post.author, PostsViewsTests.test_post.author)

    def test_group_list_page_show_correct_context(self):
        """Проверяем формирование страницы постов группы."""
        response = self.authorized_client.get(
            reverse(
                POSTS_NAMES_TEMPLATES['GROUP_LIST'][0],
                kwargs={'slug': PostsViewsTests.group.slug}
            )
        )
        self.assertEqual(
            response.context['group'],
            PostsViewsTests.group
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, PostsViewsTests.test_post.text)
        self.assertEqual(post.group, PostsViewsTests.test_post.group)
        self.assertEqual(post.author, PostsViewsTests.test_post.author)

    def test_profile_page_show_correct_context(self):
        """Проверяем формирование страницы профиля пользователя."""
        response = self.authorized_client.get(
            reverse(
                POSTS_NAMES_TEMPLATES['PROFILE'][0],
                kwargs={'username': PostsViewsTests.user.username}
            )
        )
        self.assertEqual(response.context['author'], PostsViewsTests.user)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, PostsViewsTests.test_post.text)
        self.assertEqual(post.group, PostsViewsTests.test_post.group)
        self.assertEqual(post.author, PostsViewsTests.test_post.author)

    def test_post_detail_page_show_correct_context(self):
        """Проверяем формирование страницы поста."""
        response = self.authorized_client.get(
            reverse(
                POSTS_NAMES_TEMPLATES['DETAIL'][0],
                kwargs={'post_id': '1'}
            )
        )
        self.assertEqual(response.context['post'], PostsViewsTests.test_post)

    def test_post_create_page_show_correct_context(self):
        """Проверяем формирование страницы создания поста."""
        response = self.authorized_client.get(
            reverse(POSTS_NAMES_TEMPLATES['CREATE'][0])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_field)

    def test_post_edit_page_show_correct_context(self):
        """Проверяем формирование страницы редактирования поста."""
        response = self.authorized_client.get(
            reverse(POSTS_NAMES_TEMPLATES['EDIT'][0], kwargs={'post_id': '1'})
        )
        self.assertTrue(response.context['is_edit'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_field)

    def test_index_paginator(self):
        """Проверяем паджинатор."""
        response = self.authorized_client.get(
            reverse(POSTS_NAMES_TEMPLATES['INDEX'][0])
        )
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
        response = self.authorized_client.get(
            reverse(POSTS_NAMES_TEMPLATES['INDEX'][0]) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            NUM_OF_POSTS - POSTS_PER_PAGE
        )
