# Generated by Django 2.2.9 on 2022-12-06 13:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002_auto_20221202_1903"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="group",
            options={
                "verbose_name": "Group",
                "verbose_name_plural": "Groups",
            },
        ),
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-pub_date"]},
        ),
        migrations.AlterField(
            model_name="group",
            name="description",
            field=models.TextField(verbose_name="group description"),
        ),
        migrations.AlterField(
            model_name="group",
            name="slug",
            field=models.SlugField(unique=True, verbose_name="slug field"),
        ),
        migrations.AlterField(
            model_name="group",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Group name"),
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Author name",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="posts",
                to="posts.Group",
                verbose_name="Group name",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="pub_date",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Publication date,time"
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="text",
            field=models.TextField(verbose_name="Post text"),
        ),
    ]
