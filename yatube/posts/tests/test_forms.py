import shutil
import tempfile

from django.conf import settings

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.user = User.objects.create_user(username='auth')
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_post_create(self):
        """Проверяем, что форма создаёт пост"""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )
        form = {
            'text': 'Тестовый пост_1',
            'group': PostFormTests.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args={PostFormTests.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Проверяем, что валидная форма изменяет пост"""
        posts_count = Post.objects.count()
        group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug-2',
            description='Тестовое описание_2'
        )
        uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )
        form = {
            'text': 'Тестовый пост_2',
            'group': group_2.id,
            'image': uploaded_2,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args={PostFormTests.post.id}
            ),
            data=form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args={PostFormTests.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=form['text'],
                group=form['group'],
            ).exists()
        )
