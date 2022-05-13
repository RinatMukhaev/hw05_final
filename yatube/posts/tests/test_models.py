from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

        cls.test_model = (
            (cls.group, cls.group.title),
            (cls.post, cls.post.text[:15]),
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.post.author,
            text='Новая запись!',
        )

    def test_models_str_return(self):
        """Проверка работы метода __str__ моделей."""
        for model_name, str_value in PostModelTest.test_model:
            with self.subTest(model_name=model_name):
                self.assertEqual(str(model_name), str_value)

    def test_title_label_post(self):
        """ Проверка verbose_name при создании поста."""
        task = PostModelTest.post
        verbose = task._meta.get_field('group').verbose_name
        self.assertEqual(verbose, 'Группа')

    def test_title_help_text_post(self):
        """ Проверка help_text при выборе группы."""
        task = PostModelTest.post
        help_texts = task._meta.get_field('group').help_text
        self.assertEqual(help_texts, 'Выберите название группы')

    def test_title_label_group(self):
        """ Проверка наличия verbose_name при создании группы."""
        task = PostModelTest.group
        verbose = task._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Заголовок группы')

    def test_title_help_text_group(self):
        """ Проверка наличия help_text при создании группы."""
        task = PostModelTest.group
        help_texts = task._meta.get_field('title').help_text
        self.assertEqual(help_texts, 'Укажите заголовок группы')

    def test_comment_author_help_text(self):
        """ Проверка наличия help_text (подсказки), в поле author"""
        task = PostModelTest.comment
        verbose = task._meta.get_field('author').help_text
        self.assertEqual(verbose, 'Автор отображается на сайте')

    def test_comment_post_help_text(self):
        """ Проверка наличия help_text (подсказки), в поле post"""
        task = PostModelTest.comment
        verbose = task._meta.get_field('post').help_text
        self.assertEqual(verbose, 'Под каким постом оставлен комментарий')

    def test_comment_post_verbose_name(self):
        """ Проверка наличия verbose_name, в поле post"""
        task = PostModelTest.comment
        verbose = task._meta.get_field('post').verbose_name
        self.assertEqual(verbose, 'Пост')

    def test_comment_author_verbose_name(self):
        """ Проверка наличия verbose_name, в поле author"""
        task = PostModelTest.comment
        verbose = task._meta.get_field('author').verbose_name
        self.assertEqual(verbose, 'Автор комментария')
