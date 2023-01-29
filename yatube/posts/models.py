from django.contrib.auth import get_user_model
from django.db import models

from constants import SYMBOLS_LIMIT

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Группа", max_length=200)
    slug = models.SlugField(verbose_name="slug field", unique=True)
    description = models.TextField(verbose_name="group description")

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст поста",
    )
    pub_date = models.DateTimeField(
        verbose_name="Publication date,time", auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name="Author name",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        related_name="posts",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Выберите группу",
    )

    image = models.ImageField(
        verbose_name="Картинка", upload_to="posts/", blank=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:SYMBOLS_LIMIT]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name="Пост",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Введите текст комментария",
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:SYMBOLS_LIMIT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following",
    )
