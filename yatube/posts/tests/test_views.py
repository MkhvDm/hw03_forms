from http import HTTPStatus

import django.core.paginator
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from django.core.paginator import Paginator
from django.conf import settings

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='Im_author')
        cls.user_not_author = User.objects.create(username='Im_not_author')
        cls.num_of_test_groups = 3
        cls.groups = [None, ]
        for i in range(cls.num_of_test_groups):
            cls.groups.append(
                Group.objects.create(
                    title=f'Тестовая группа {i}',
                    slug=f'test-group-slug-{i}',
                    description=f'Тестовое описание {i}',
                )
            )
        # print('\nGROUPS:')
        # print(cls.groups)
        cls.num_of_test_posts = 23
        cls.posts = []
        for i in range(cls.num_of_test_posts):
            cls.posts.append(Post.objects.create(
                author=cls.user_author,
                text=f'Тестовый пост {i}',
                group=cls.groups[i % cls.num_of_test_groups]
            ))
        # print('\nPOSTS:')
        # print(cls.posts[0].group,
        #       cls.posts[1].group,
        #       cls.posts[2].group,
        #       cls.posts[3].group,
        #       cls.posts[4].group, sep='\n')

    def setUp(self) -> None:
        self.guest_client = Client()

        self.author_client = Client()
        self.author_client.force_login(PostViewsTests.user_author)

        self.not_author_client = Client()
        self.not_author_client.force_login(PostViewsTests.user_not_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list',
                        kwargs={'slug': 'test-group-slug-0'}),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': PostViewsTests.user_author}),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': 1})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': 1})
            ),
            'posts/create_post.html':  reverse('posts:post_create'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def custom_util_for_check_types_in_context(self):
        pass

    # index testing:
    def test_index_context_types(self):
        """Проверка, что в контекст index'а передаются объекты верных типов."""
        response = self.guest_client.get(reverse('posts:index'))
        expected_types = {
            'title': str,
            'page_obj': django.core.paginator.Page,
            'group_link_is_visible': bool
        }
        for context_key, context_type in expected_types.items():
            with self.subTest(context_key=context_key):
                self.assertIsInstance(
                    response.context[context_key],
                    context_type)

    def test_index_page_1_context(self):
        """Число постов на 1 странице index равно N (default: 10)."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUM_OF_POSTS_ON_PAGE)

    def test_index_last_page_context(self):
        """Число постов на последней странице index равно %10 (default: 10)."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUM_OF_POSTS_ON_PAGE)

    # group testing:
    def test_group_context_types(self):
        pass

    def test_group_page_1_context(self):
        pass

    def test_group_last_page_context(self):
        pass

    def test_unexist_group_slug(self):
        # redirect 404
        pass


