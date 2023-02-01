import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm,
from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Test_User")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост",
            group=cls.group,
            author=cls.user,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.guest = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(PostFormsTests.user)

    def test_create_post(self):
        """Проверка что пост сохранился в базе данных."""
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "Тестовый пост создан",
            "group": self.group.pk,
            "author": self.user,
            "image": uploaded,
        }
        response = self.authorized_user.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", args=(self.user.username,))
        )
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый пост создан",
                group=self.group.pk,
                image="posts/small.gif",
                author=self.user,
            ).exists()
        )

    def test_post_edit(self):
        """Проверка что пост с id был изменен через post_edit."""
        post_edit_data = {
            "text": "Тестовый редактированный пост",
            "group": self.group.pk,
            "author": self.user,
        }
        response = self.authorized_user.post(
            reverse("posts:post_edit", args=(self.post.pk,)),
            data=post_edit_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                id=PostFormsTests.post.pk,
                text="Тестовый редактированный пост",
                group=PostFormsTests.group.pk,
                author=PostFormsTests.user,
            ).exists()
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", args=(self.post.pk,))
        )

    def test_comment_authorized(self):
        """Проверка создания коментария
        авторизированным пользователем."""
        form_data = {"text": "Test comment"}
        self.authorized_user.post(
            reverse(
                "posts:add_comment",
                kwargs={
                    "post_id": self.post.pk,
                },
            ),
            data=form_data,
            follow=True,
        )
        self.assertTrue(Comment.objects.filter(text="Test comment").exists())

    def test_comment_guest(self):
        """Проверка создания коментария
        неавторизированным пользователем."""
        form_data = {"text": "Test comment"}
        self.guest.post(
            reverse(
                "posts:add_comment",
                kwargs={
                    "post_id": self.post.pk,
                },
            ),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Comment.objects.filter(text="Test comment").exists())
