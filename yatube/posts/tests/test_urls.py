from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаём экземпляр user, group & post."""
        super().setUpClass()
        cls.user_author = User.objects.create(username='Im_author')
        cls.user_not_author = User.objects.create(username='Im_not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self) -> None:
        self.guest_client = Client()

        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user_author)

        self.not_author_client = Client()
        self.not_author_client.force_login(PostURLTests.user_not_author)

    def test_auth_non_required_urls(self):
        """Тестировнаие общедоступных страниц, в ответ ожидаем код 200."""
        url_template_names = {
            '/': 'posts/index.html',
            '/group/test-group-slug/': 'posts/group_list.html',
            '/profile/Im_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for url, template_name in url_template_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'[!] Нет ответа по адресу {url}!')

    def test_auth_required_urls(self):
        """Тестировнаие страниц, требующих авторизации."""
        urls = (
            '/posts/1/edit/',
            '/create/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'[!] Нет ответа по адресу {url}!')

    def test_redirect_auth_required_urls(self):
        """Проверка переадресации на страницах, требующих авторизации."""
        redirect_urls_trace = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/'
        }
        for url, redirect_url in redirect_urls_trace.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_redirect_author_required_urls(self):
        """Проверка переадресации, требующих авторства."""
        url = '/posts/1/edit/'
        redirect_url = '/posts/1/'
        response = self.not_author_client.get(url, follow=True)
        self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        """Тест, что URL-адрес использует соответствующий шаблон."""
        url_templates = {
            '/': 'posts/index.html',
            '/group/test-group-slug/': 'posts/group_list.html',
            '/profile/Im_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in url_templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response, template,
                    (f'Страница по адресу {url} должна использовать '
                     f'шаблон {template}!')
                )

    def test_unexisting_url(self):
        """Запрос на несуществующий в проекте URL."""
        url = '/unexisting_url/'
        response = self.not_author_client.get(url)
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND,
            'По несуществующему адресу код ответа должен быть 404!')
