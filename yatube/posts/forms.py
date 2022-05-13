from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group"]
        help_texts = {
            'text': ('Данное поле предназначено для Вашей записи.'),
            'group': ('Группа записей ,'
                      'в которой Вы разместите свой пост.'),
        }
        verbose_name = 'Пост'
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
