from django.contrib.auth import get_user_model
from django.test import TestCase

from constants import SYMBOLS_LIMIT

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание группы больше 15 символов",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост с длиной больше 15 символов",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post_text = PostModelTest.post
        group_name = PostModelTest.group
        self.assertEqual(post_text.__str__(), post_text.text[:SYMBOLS_LIMIT])
        self.assertEqual(group_name.__str__(), "Тестовая группа")
