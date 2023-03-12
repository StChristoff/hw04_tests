from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_post_create(self):
        """Проверяем, что форма создаёт пост"""
        posts_count = Post.objects.count()
        form = {
            'text': 'Тестовый пост_2',
            'group': PostFormTests.group.id,
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
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id + 1,
                text=form['text'],
                group=form['group'],
            ).exists()
        )

    def test_post_edit(self):
        """Проверяем, что валидная форма изменяет пост"""
        posts_count = Post.objects.count()
        group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug-2',
            description='Тестовое описание_2'
        )
        form = {
            'text': 'Тестовый пост_3',
            'group': group_2.id,
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
