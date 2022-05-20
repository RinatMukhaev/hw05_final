from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from posts.models import Group, Post, Follow, Comment
import tempfile
import shutil
from django.conf import settings

User = get_user_model()
COUNT_POSTS = 12
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class YatubePagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')
        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='test_slug',
            description='Группа Льва Толстого'
        )
        cls.post = Post.objects.create(
            group=YatubePagesTests.group,
            author=cls.user,
            text='Текст',
        )
        cls.author = User.objects.create_user(
            username='New User', email='test@gmail.com', password='test_pass'
        )
        cls.client_auth_follower = Client()
        cls.client_auth_following = Client()
        cls.user_follower = User.objects.create_user(
            username='follower',
            email='test_11@mail.ru',
            password='test_pass'
        )
        cls.user_following = User.objects.create_user(
            username='following',
            email='test22@mail.ru',
            password='test_pass'
        )
        cls.client_auth_follower.force_login(cls.user_follower)
        cls.client_auth_following.force_login(cls.user_following)
        cls.url_index = reverse('posts:index')
        cls.url_group = reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}
        )
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': f'{cls.user}'}
        )
        cls.url_post_detail = reverse(
            'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}
        )
        cls.url_post_creat = reverse('posts:post_create')
        cls.url_post_edit = reverse(
            'posts:post_edit', kwargs={'post_id': f'{cls.post.id}'}
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """"URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_detail: 'posts/post_detail.html',
            self.url_post_creat: 'posts/create_post.html',
            self.url_post_edit: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """
        Шаблон index сформирован с правильным контекстом.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            group=YatubePagesTests.group,
            author=self.user,
            text='Текст',
            image=uploaded
        )
        response = self.authorized_client.get(self.url_index)
        first_object = response.context["page_obj"][0]
        self.assertEqual(first_object.text, 'Текст')
        self.assertEqual(first_object.author.username, 'NewUser')
        self.assertContains(response, 'image')

    def test_group_pages_show_correct_context(self):
        """
        Шаблон group сформирован с правильным контекстом.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            group=YatubePagesTests.group,
            author=self.user,
            text='Текст',
            image=uploaded
        )
        response = self.authorized_client.get(self.url_group)
        self.assertEqual(
            response.context.get('group').title, 'Лев Толстой'
        )
        self.assertEqual(
            response.context.get('group').description, 'Группа Льва Толстого'
        )
        self.assertEqual(response.context.get('group').slug, 'test_slug')
        self.assertContains(response, 'image')

    def test_profile_pages_show_correct_context(self):
        """
        Шаблон profile сформирован с правильным контекстом.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            group=YatubePagesTests.group,
            author=self.user,
            text='Текст',
            image=uploaded
        )
        response = self.authorized_client.get(self.url_profile)
        post = response.context['page_obj'][0]
        author = response.context['author']
        self.assertEqual(author.username, 'NewUser')
        self.assertEqual(post.text, 'Текст')
        self.assertContains(response, 'image')

    def test_post_detail_pages_show_correct_context(self):
        """
        Шаблон post_detail сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(self.url_post_detail)
        post = response.context['post']
        self.assertEqual(post.text, 'Текст')

    def test_post_edit_pages_show_correct_context(self):
        """
        Шаблон post_edit сформирован с правильным контекстом.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            group=YatubePagesTests.group,
            author=self.user,
            text='Текст',
            image=uploaded
        )
        response = self.authorized_client.get(self.url_post_edit)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_creat_pages_show_correct_context(self):
        """
        Шаблон post_creat сформирован с правильным контекстом.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            group=YatubePagesTests.group,
            author=self.user,
            text='Текст',
            image=uploaded
        )
        response = self.authorized_client.get(self.url_post_creat)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_in_page_show_correct(self):
        """
        Пост отображается на главной странице,
        странице группы и профиле пользователя.
        """
        list_urls = tuple((self.url_index, self.url_group, self.url_profile,))
        for reverse_name in list_urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, 'Текст')
                self.assertEqual(first_object.group.title, 'Лев Толстой')
                self.assertContains(response, 'image')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            group=YatubePagesTests.group,
            author=self.user,
            text='Текст',
            image=uploaded
        )

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_on_first_page = 10
        posts_on_second_page = 3
        posts = [
            Post(
                author=self.user, text=self.post.text, group=self.group
            ) for i in range(COUNT_POSTS)
        ]
        Post.objects.bulk_create(posts)
        list_urls = tuple((self.url_index, self.url_group, self.url_profile,))
        pages = ((1, posts_on_first_page), (2, posts_on_second_page))
        for reverse_name in list_urls:
            with self.subTest(reverse_name=reverse_name):
                for page, count in pages:
                    response = self.guest_client.get(
                        reverse_name, {'page': page, }
                    )
                    self.assertEqual(len(response.context['page_obj']), count)

    def test_only_authorized_user_add_comment(self):
        """Только авторизованный пользователь может добавлять комментарии."""
        comments_count = Comment.objects.count()
        path = reverse(
            'posts:add_comment', kwargs={'post_id': f'{self.post.id}'}
        )
        data = {'text': 'Комментарий'}

        self.guest_client.post(path, data, follow=True)
        self.assertEqual(Comment.objects.count(), comments_count)

        self.authorized_client.post(path, data, follow=True)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_follow(self):
        """Проверка подписок."""
        self.client_auth_follower.get(reverse(
            'posts:profile_follow', kwargs={
                'username': self.user_following.username
            })
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Проверка отписок."""
        self.client_auth_follower.get(reverse(
            'posts:profile_follow', kwargs={
                'username': self.user_following.username
            }
        ))
        self.client_auth_follower.get(reverse(
            'posts:profile_unfollow', kwargs={
                'username': self.user_following.username
            })
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )

        """запись появляется в ленте подписчиков"""
        Follow.objects.create(
            user=self.user_follower, author=self.user_following
        )
        response = self.client_auth_follower.get('/follow/')
        self.assertEqual(
            response.context["page_obj"][0].text,
            'Тестовая запись для тестирования ленты'
        )
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(
            response, 'Тестовая запись для тестирования ленты'
        )
        self.assertTrue(self.author, self.user_following)
        self.assertTrue(self.user, self.user_follower)

    def test_cache_index_test(self):
        """Тест кэширования страницы index.html."""
        first_state = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.delete()
        second_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(second_state.content, third_state.content)
