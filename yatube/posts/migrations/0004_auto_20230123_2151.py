# Generated by Django 2.2.16 on 2023-01-23 18:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0003_auto_20221206_1655"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Группа"),
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
                verbose_name="Группа",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="text",
            field=models.TextField(verbose_name="Текст поста"),
        ),
    ]
