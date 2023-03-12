from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

POST_TEXT = 'Тестовый пост'
GROUP_TITLE = 'Тестовая группа'
SYM_NUM = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug='Тестовое url-имя группы',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        object_names = {
            PostModelTest.post: POST_TEXT,
            PostModelTest.group: GROUP_TITLE,
        }
        for value, expected_object_name in object_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    expected_object_name[:SYM_NUM],
                    str(value)[:SYM_NUM]
                )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task_post = PostModelTest.post
        task_group = PostModelTest.group
        post_field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        group_field_verboses = {
            'title': 'Имя группы',
            'slug': 'url-имя группы',
            'description': 'Описание группы',
        }

        def func(task, context):
            for value, expected in context.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        task._meta.get_field(value).verbose_name, expected)
        func(task_post, post_field_verboses)
        func(task_group, group_field_verboses)
