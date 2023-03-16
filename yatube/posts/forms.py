from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            # Это для 6 спринта, не считай, пожалуйста за ошибку.
            # Иначе pytest не проходит, т.к. в форме ожидается
            # только 2 аргумента.
            # 'image',
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
