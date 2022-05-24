from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаём экземпляр user, group & post."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_obj_name = PostModelTest.post.text[:15]
        self.assertEqual(
            expected_obj_name,
            str(PostModelTest.post),
            f'[!] Метод __str__ у модели Post работает неверно!'
        )

    def test_verbose_names(self):
        """Проверяем, что у полей модели Post верные verbose_name."""
        field_verboses = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_verbose_name in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_verbose_name,
                    '[x] Значение verbose_name не соответствует ожидаемому.'
                )

    def test_help_text(self):
        """Проверяем, что у полей модели Post верные help_text."""
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_help_text in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_help_text,
                    '[x] Значение help_text не соответствует ожидаемому.'
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаём экземпляр user, group & post."""
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_obj_name = GroupModelTest.group.title
        self.assertEqual(
            expected_obj_name,
            str(GroupModelTest.group),
            f'[!] Метод __str__ у модели Group работает неверно!'
        )

