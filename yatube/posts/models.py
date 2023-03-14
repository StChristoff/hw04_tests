from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

SYM_NUM = 15


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
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
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:SYM_NUM]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Имя группы',
    )
    slug = models.SlugField(unique=True, verbose_name='url-имя группы')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title
