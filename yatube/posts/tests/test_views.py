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
        cls.num_of_test_groups = 2

        for i in range(cls.num_of_test_groups):
            Group.objects.create(
                title=f'Тестовая группа {i}',
                slug=f'test-group-slug-{i}',
                description=f'Тестовое описание {i}',
            )
        cls.groups = [None, Group.objects.get(pk=1), Group.objects.get(pk=2)]

            # cls.groups.append(
            #     Group.objects.create(
            #         title=f'Тестовая группа {i}',
            #         slug=f'test-group-slug-{i}',
            #         description=f'Тестовое описание {i}',
            #     )
            # )

        cls.num_of_test_posts = 33  # required 33+, recommended not x10
        cls.posts = []
        for i in range(cls.num_of_test_posts):
            Post.objects.create(
                author=cls.user_author,
                text=f'Тестовый пост {i}',
                group=cls.groups[i % cls.num_of_test_groups]
            )
            # cls.posts.append(Post.objects.create(
            #     author=cls.user_author,
            #     text=f'Тестовый пост {i}',
            #     group=cls.groups[i % cls.num_of_test_groups]
            # ))
        # print('\nPOSTS:', cls.posts)
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
        """В контекст index'а передаются объекты верных типов."""
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
        """Число постов на последней странице index равно %N (default: 10)."""
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

    # group testing:
    def test_group_context_types(self):
        """В контекст group_list'а передаются объекты верных типов."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-group-slug-0'})
        )
        expected_types = {
            'group': Group,
            'page_obj': django.core.paginator.Page,
            'group_link_is_visible': bool
        }
        for context_key, context_type in expected_types.items():
            with self.subTest(context_key=context_key):
                self.assertIsInstance(
                    response.context[context_key],
                    context_type)

    # def test_group_page_1_context(self):
    #     pass

    def test_group_last_page_context(self):
        group_slug = 0
        n_posts = PostViewsTests.num_of_test_posts
        print('\nPOSTS:', n_posts)
        n_groups = PostViewsTests.num_of_test_groups
        print('GROUPS:', n_groups)
        posts_on_page = settings.NUM_OF_POSTS_ON_PAGE

        n_group_posts = (n_posts + (n_groups - 1)) // (n_groups + 1)
        print('GROUP POSTS:', n_group_posts)
        last_page_num = (n_group_posts + (posts_on_page - 1)) // posts_on_page
        expected_last_page_posts_num = (
            posts_on_page
            if not (n_group_posts % posts_on_page)
            else n_group_posts % posts_on_page
        )
        print('LAST PAGE:', last_page_num)
        print('EXPECTED GROUP POSTS:', expected_last_page_posts_num)
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'test-group-slug-{group_slug}'}
            ) + f'?page={last_page_num}')
        print('RESPONSE LEN POSTS:', len(response.context['page_obj']))
        for post in response.context['page_obj']:
            print()
            print(post)
        # print('RESPONSE POSTS:', response.context['page_obj'])

        self.assertEqual(
            len(response.context['page_obj']),
            expected_last_page_posts_num)


    #
    # def test_group_last_page_context(self):
    #     pass
    #
    # def test_unexist_group_slug(self):
    #     # redirect 404
    #     pass


