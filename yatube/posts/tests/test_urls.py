from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLtests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст поста",
        )
        cls.templates = [
            "/",
            f"/group/{cls.group.slug}/",
            f"/profile/{cls.user}/",
            f"/posts/{cls.post.pk}/",
        ]
        cls.template_url_names = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.user.username}/": "posts/profile.html",
            f"/posts/{cls.post.pk}/": "posts/post_detail.html",
            f"/posts/{cls.post.pk}/edit/": "posts/post_create.html",
            "/create/": "posts/post_create.html",
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = self.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_for_all_users(self):
        """Страницы index, group, profile, detail
        доступны всем пользователям."""
        for adress in self.templates:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_authorized(self):
        """Страница create доступна авторизированному пользователю."""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_for_author(self):
        """Страница редактирования поста доступна только автору."""
        self.user = User.objects.get(username=self.user)
        response = self.authorized_client.get(f"/posts/{self.post.pk}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_unauthorised_user(self):
        """Страница create перенаправляет неавторизированного
        пользователя на страницу авторизации."""
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответсвующий шаблон."""
        for address, template in self.template_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_not_found(self):
        """При вызове страницы с несуществующим URL, выводит ошибку 404."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
