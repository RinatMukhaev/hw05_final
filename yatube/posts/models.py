from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import Truncator

User = get_user_model()

N_WORDS = 3


class Group(models.Model):
    title = models.CharField(
        max_length=200, verbose_name='Заголовок группы',
        help_text='Укажите заголовок группы'
    )
    slug = models.SlugField(
        unique=True, verbose_name="Slug (идентификатор)",
        help_text="Slug это уникальная строка"
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='У группы должно быть описание'
    )

    def __str__(self):
        return Truncator(self.title).words(
            N_WORDS, truncate=" ...")


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Обязательное поле'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
        help_text="Выберите имя автора"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='group_posts',
        verbose_name="Группа",
        help_text="Выберите название группы"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='Пост',
                             help_text='Под каким постом оставлен комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария',
                               help_text='Автор отображается на сайте')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text=('Обязательное поле'))
    created = models.DateTimeField(verbose_name='Дата публикации',
                                   help_text='Дата публикации',
                                   auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии к постам'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
