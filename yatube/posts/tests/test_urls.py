from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.author = User.objects.create_user(
            username='HasNoname',
            email='testuser@yatube.ru',
            password='test_pass'
        )
        cls.template_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            f'/profile/{cls.user}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        cls.urls_for_guest = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user}/',
            f'/posts/{cls.post.id}/',
        ]
        cls.urls_for_authorized = [
            '/create/',
            f'/posts/{cls.post.id}/edit/',
        ]

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соотвествующие шаблоны."""
        for address, template in StaticURLTests.template_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unauthorized_user_urls_status_code(self):
        """Страницы доступные любому пользователю."""
        for url in StaticURLTests.urls_for_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_creat_and_post_edit_url_redirect_guest_client(self):
        """Страницы перенаправляющие анонимного пользователя."""
        login = reverse('login')
        for url in StaticURLTests.urls_for_authorized:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'{login}?next={url}')

    def test_post_edit_page_redirect_guest_client_test(self):
        """Проверка переадресации с страницы post/edit."""
        for url in StaticURLTests.urls_for_authorized:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_404_page(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response = self.guest_client.get('/n0t_ex15ting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
