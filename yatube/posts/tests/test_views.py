import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.user_2 = User.objects.create_user(username="test_user_2")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.gorup_1 = Group.objects.create(
            title="Тестовая непринадлежащая группа",
            slug="test_1_slug",
            description="Тест непринадлежности к группе",
        )
        image = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=image, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Тестовый пост",
            group=cls.group,
            author=cls.user,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_client = Client()
        self.new_client.force_login(self.user_2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_posts", args=(self.group.slug,)
            ): "posts/group_list.html",
            reverse(
                "posts:profile", args=(self.user.username,)
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", args=(self.post.pk,)
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", args=(self.post.pk,)
            ): "posts/post_create.html",
            reverse("posts:post_create"): "posts/post_create.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        first_objects = response.context["page_obj"][0]
        post_text = first_objects.text
        post_group = first_objects.group
        post_author = first_objects.author
        post_image = first_objects.image
        self.assertEqual(post_text, "Тестовый пост")
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_image, self.post.image)

    def test_group_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        one_object = response.context["group"]
        two_object = response.context["page_obj"][0]
        self.assertEqual(one_object.title, self.group.title)
        self.assertEqual(one_object.slug, self.group.slug)
        self.assertEqual(one_object.description, self.group.description)
        self.assertEqual(two_object.text, self.post.text)
        self.assertEqual(two_object.group, self.group)
        self.assertEqual(two_object.author, self.user)
        self.assertEqual(two_object.image, self.post.image)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        object = response.context["page_obj"][0]
        self.assertEqual(object.text, self.post.text)
        self.assertEqual(object.author, self.user)
        self.assertEqual(object.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        object = response.context["post"]
        self.assertEqual(object.text, self.post.text)
        self.assertEqual(object.pub_date, self.post.pub_date)
        self.assertEqual(object.group, self.post.group)
        self.assertEqual(object.author, self.post.author)
        self.assertEqual(object.image, self.post.image)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_belongs_page(self):
        """При создании поста с группой, он появляется
        на страницах и попадает в свою группу."""
        post_pages = (
            reverse("posts:index"),
            reverse("posts:group_posts", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        )
        for page in post_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                object = response.context["page_obj"][0]
                self.assertEqual(object.text, self.post.text)
                self.assertEqual(object.group, self.group)
                self.assertNotEqual(object.group, self.gorup_1)

    def test_comment_belongs_post(self):
        """При добавлении коментария позльзователем
        он появляется на странице поста."""
        form_data = {
            "text": "Текст комментария",
        }
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", args=(self.post.pk,))
        )
        self.assertTrue(
            Comment.objects.filter(text="Текст комментария").exists()
        )

    def test_guest_user(self):
        """Неавторизированный пользователь не создает комментарий."""
        form_data = {
            "text": "Неавторизированный комментарий",
        }
        self.guest_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertFalse(
            Comment.objects.filter(
                text="Неавторизированный комментарий"
            ).exists()
        )

    def test_post_index_cache(self):
        """Проверка кеша."""
        response_1 = self.authorized_client.get(reverse("posts:index"))
        cache.clear()
        response_2 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_1.content, response_2.content)
        response_3 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_1.content, response_3.content)

    def test_authorized_user_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок."""
        # У пользователя нет подписок на автора
        response = self.new_client.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post, response.context["page_obj"])
        # Создали подписку и проверили ее наличие у пользователя
        Follow.objects.get_or_create(user=self.user_2, author=self.post.author)
        response_2 = self.new_client.get(reverse("posts:follow_index"))
        self.assertIn(self.post, response_2.context["page_obj"])
        # Отменили подписку и проверили что ее нет у пользователя
        Follow.objects.filter(
            user=self.user_2, author=self.post.author
        ).delete()
        response_3 = self.new_client.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post, response_3.context["page_obj"])

    def test_new_post_follow(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        Follow.objects.get_or_create(user=self.user_2, author=self.post.author)
        new_post = Post.objects.create(
            text="Тестовый пост_222",
            group=self.group,
            author=self.post.author,
        )
        outer_client = User.objects.create(username="Blank")
        self.authorized_client.force_login(outer_client)
        response_1 = self.new_client.get(reverse("posts:follow_index"))
        response_2 = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertIn(new_post, response_1.context["page_obj"])
        self.assertNotIn(new_post, response_2.context["page_obj"])


class PostPaginationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Test_User")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = []
        for i in range(13):
            cls.post.append(
                Post.objects.create(
                    text=f"Тестовый пост {i}",
                    group=cls.group,
                    author=cls.user,
                )
            )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """Корректная паджинация на странице index."""

        response = self.client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_index_second_page_contains_three_records(self):
        """Корректная паджинация на странице index."""
        response = self.client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Корректная паджинация на странице group_list."""
        response = self.client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_group_list_second_page_contains_three_records(self):
        """Корректная паджинация на странице group_list."""
        response = self.client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_profile_first_page_contains_ten_records(self):
        """Корректная паджинация на странице profile."""
        response = self.client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_profile_page_contains_three_records(self):
        """Корректная паджинация на странице profile."""
        response = self.client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)
