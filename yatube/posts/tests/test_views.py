from http import HTTPStatus

import django.core.paginator
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from django.core.paginator import Page
from django.conf import settings

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.num_of_authors = 2
        cls.user_author = User.objects.create(username='Im_author')
        cls.user_author_too = User.objects.create(username='Im_author_too')
        cls.user_not_author = User.objects.create(username='Im_not_author')
        cls.authors = [cls.user_author, cls.user_author_too]

        cls.num_of_test_groups = 2
        cls.groups = [None, ]
        for i in range(cls.num_of_test_groups):
            cls.groups.append(
                Group.objects.create(
                    title=f'Тестовая группа {i}',
                    slug=f'test-group-slug-{i}',
                    description=f'Тестовое описание {i}',
                )
            )
        #     Group.objects.create(
        #         title=f'Тестовая группа {i}',
        #         slug=f'test-group-slug-{i}',
        #         description=f'Тестовое описание {i}',
        #     )
        # cls.groups = [None, Group.objects.get(pk=1), Group.objects.get(pk=2)]

        cls.num_of_test_posts = 33  # required 33+, recommended not x10
        cls.posts = []
        for i in range(cls.num_of_test_posts):
            cls.posts.append(Post.objects.create(
                author=cls.authors[i % cls.num_of_test_groups],
                text=f'Тестовый пост {i}',
                group=cls.groups[i % (cls.num_of_test_groups + 1)]
            ))
            # Post.objects.create(
            #     id=i,
            #     author=cls.user_author,
            #     text=f'Тестовый пост {i}',
            #     group=cls.groups[i % (cls.num_of_test_groups + 1)]
            # )

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
        """В контекст index'а передаются объекты верных типов."""
        response = self.guest_client.get(reverse('posts:index'))
        expected_types = {
            'title': str,
            'page_obj': Page,
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
        """На последней странице index верное число постов %N."""
        n_posts = PostViewsTests.num_of_test_posts
        posts_on_page = settings.NUM_OF_POSTS_ON_PAGE
        last_page_num = (n_posts + (posts_on_page - 1)) // posts_on_page
        expected_last_page_posts_num = (
            posts_on_page
            if not (n_posts % posts_on_page)
            else n_posts % posts_on_page
        )
        response = self.guest_client.get(
            reverse('posts:index') + f'?page={last_page_num}')
        self.assertEqual(
            len(response.context['page_obj']),
            expected_last_page_posts_num)

    # group_list testing:
    def test_group_context_types(self):
        """В контекст group_list'а передаются объекты верных типов."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group-slug-0'})
        )
        expected_types = {
            'group': Group,
            'page_obj': Page,
            'group_link_is_visible': bool
        }
        for context_key, context_type in expected_types.items():
            with self.subTest(context_key=context_key):
                self.assertIsInstance(
                    response.context[context_key],
                    context_type)

    def test_correct_group_selecting(self):
        """На странице group_list посты только определённой группы."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group-slug-0'})
        )
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertEqual(post.group.slug, 'test-group-slug-0')

    def test_group_page_1_context(self):
        """Число постов на 1 странице group_list равно N (default: 10)."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group-slug-0'})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUM_OF_POSTS_ON_PAGE
        )

    def test_group_last_page_context(self):
        """На последней странице group_list верное число постов."""
        group_slug = 0
        n_posts = PostViewsTests.num_of_test_posts
        n_groups = PostViewsTests.num_of_test_groups
        posts_on_page = settings.NUM_OF_POSTS_ON_PAGE

        n_group_posts = (n_posts + (n_groups - 1)) // (n_groups + 1)
        last_page_num = (n_group_posts + (posts_on_page - 1)) // posts_on_page
        expected_last_page_posts_num = (
            posts_on_page
            if not (n_group_posts % posts_on_page)
            else n_group_posts % posts_on_page
        )
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'test-group-slug-{group_slug}'}
            ) + f'?page={last_page_num}')

        self.assertEqual(
            len(response.context['page_obj']),
            expected_last_page_posts_num)

    def test_unexist_group_slug(self):
        """Переадресация при запросе group_list несуществующей группы."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'unexist-slug'}),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # profile testing:
    def test_profile_context_types(self):
        """В контекст profile'а передаются объекты верных типов."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'Im_author'})
        )
        expected_types = {
            'page_obj': Page,
            'author': User,
            'group_link_is_visible': bool
        }
        for context_key, context_type in expected_types.items():
            with self.subTest(context_key=context_key):
                self.assertIsInstance(
                    response.context[context_key],
                    context_type)

    def test_correct_profile_selecting(self):
        """На странице profile посты только определённого автора."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'Im_author'})
        )
        for post in response.context['page_obj']:
            with self.subTest(post=post):
                self.assertEqual(post.author.username, 'Im_author')

    def test_profile_page_1_context(self):
        """Число постов на 1 странице profile равно N (default: 10)."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'Im_author'})
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.NUM_OF_POSTS_ON_PAGE
                         )

    def test_profile_last_page_context(self):
        """На последней странице profile верное число постов."""
        n_posts = PostViewsTests.num_of_test_posts
        posts_on_page = settings.NUM_OF_POSTS_ON_PAGE
        n_author_posts = (n_posts // 2) + 1 if n_posts % 2 else n_posts // 2
        last_page_num = (n_author_posts + (posts_on_page - 1)) // posts_on_page
        expected_last_page_posts_num = (
            posts_on_page
            if not (n_author_posts % posts_on_page)
            else n_author_posts % posts_on_page
        )
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'Im_author'})
            + f'?page={last_page_num}')
        self.assertEqual(
            len(response.context['page_obj']),
            expected_last_page_posts_num)

    # post_detail testing:
    def test_post_detail_context_types(self):
        """В контекст post_detail'а передаются объекты верных типов."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        expected_types = {'post': Post,
                          'num_posts': int}
        for context_key, context_type in expected_types.items():
            with self.subTest(context_key=context_key):
                self.assertIsInstance(
                    response.context[context_key],
                    context_type)

    def test_correct_post_detail_selecting(self):
        """На странице post_detail верный пост."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        expected_post = {
            'id': 1,
            'author': 1,  # author_id
            'group': None,
            'text': 'Тестовый пост 0'
        }
        for field, value in expected_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    response.context['post'].serializable_value(field),
                    value)

    def test_correct_num_of_authors_posts(self):
        """На странице post_detail выводится верное число постов автора."""
        author = 'Im_author'
        n_posts = PostViewsTests.num_of_test_posts
        n_author_posts = (n_posts // 2) + 1 if n_posts % 2 else n_posts // 2
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEqual(response.context.get('num_posts'), n_author_posts)

    def test_unexisting_post(self):
        """На запрос несуществующего поста возвращается ошибка 404."""
        pass

    # post_edit testing:
    # ...


    # post_create testing:
    # ...




