from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POST_TEXT = 'Тестовый пост +100500'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.SYM_NUM = 15
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug='Тестовое url-имя группы',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.POST_TEXT,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        object_names = {
            PostModelTest.post:
            PostModelTest.POST_TEXT[:PostModelTest.SYM_NUM],
            PostModelTest.group: PostModelTest.GROUP_TITLE,
        }
        for value, expected_object_name in object_names.items():
            with self.subTest(value=value):
                self.assertEqual(expected_object_name, str(value))

    def test_post_verbose_names(self):
        """verbose_name поста в поле модели совпадает с ожидаемым."""
        post_field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for value, expected in post_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_post_help_text(self):
        """help_text в полях модели post совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).help_text,
                    expected
                )

    def test_group_verbose_names(self):
        """verbose_name группы в поле модели совпадает с ожидаемым."""
        group_field_verboses = {
            'title': 'Имя группы',
            'slug': 'url-имя группы',
            'description': 'Описание группы',
        }
        for value, expected in group_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(value).verbose_name,
                    expected
                )

    def test_group_help_text(self):
        """help_text в полях модели group совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Введите имя группы',
            'slug': (
                'Укажите адрес для страницы группы. Используйте только '
                'латиницу, цифры, дефисы и знаки подчёркивания'
            ),
            'description': 'Введите описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(value).help_text,
                    expected
                )
