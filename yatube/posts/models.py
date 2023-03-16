from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

SYM_NUM = 15


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',)
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        'Group',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Загрузите картинку',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:SYM_NUM]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Имя группы',
        help_text='Введите имя группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='url-имя группы',
        help_text=(
            'Укажите адрес для страницы группы. Используйте только '
            'латиницу, цифры, дефисы и знаки подчёркивания'
        ),
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы',
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор поста',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:SYM_NUM]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Подписка на {self.author}'
