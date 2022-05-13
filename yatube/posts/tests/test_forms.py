from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.forms import PostForm, CommentForm
from posts.models import Group, Post

User = get_user_model()


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='test_slug',
            description='Группа Льва Толстого',
        )

        cls.author = User.objects.create_user(
            username='NewUser', email='test@gmail.com', password='test_pass'
        )

        cls.post = Post.objects.create(
            group=TestCreateForm.group,
            text="Текст",
            author=User.objects.get(username='NewUser'),
        )

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='New User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """
        Проверка создания нового поста, авторизированным пользователем.
        """
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Отправить текст',
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'New User'}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Отправить текст',
            group=TestCreateForm.group).exists())

    def test_form_update(self):
        """
        Проверка редактирования поста через форму на странице.
        """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        url = reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
        )
        self.authorized_client.get(url)
        form_data = {
            'group': self.group.id,
            'text': 'Обновленный текст',
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
            ), data=form_data, follow=True
        )

        self.assertTrue(Post.objects.filter(
            text='Обновленный текст',
            group=TestCreateForm.group).exists())

    def test_not_create_post_with_guest(self):
        """Проверка, что гость POST запросом не может создать пост."""
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
        }
        posts_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse(
                'posts:post_create'
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_not_edit_post_with_user_not_author(self):
        """
        Проверка, что пользователь не может изменить чужой пост.
        """
        user_editor = User.objects.create(
            username='editor_not_owner_post'
        )
        authorized_editor = Client()
        authorized_editor.force_login(user_editor)
        group = TestCreateForm.group
        test_post = Post.objects.create(
            text='Тест текста поста',
            author=TestCreateForm.author,
            group=group
        )
        test_post_id = test_post.id
        posts_count_before = Post.objects.count()
        another_group = Group.objects.create(
            title='Другая группа',
            slug='another_slug'
        )
        form_data = {
            'text': 'Текст',
            'group': another_group.id,
        }
        response = authorized_editor.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            )
        )
        db_post = Post.objects.get(id=test_post_id)
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertNotEqual(db_post.text, form_data['text'])
        self.assertNotEqual(db_post.group, form_data['group'])

    def test_comment_form_valid(self):
        """Проверяем форму комментариев."""
        form_data = {'text': 'Новый комментарий'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
