# Generated by Django 4.2.6 on 2023-11-18 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("post", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="post",
            name="origin",
        ),
        migrations.RemoveField(
            model_name="post",
            name="source",
        ),
        migrations.AddField(
            model_name="post",
            name="categories",
            field=models.ManyToManyField(to="post.category"),
        ),
    ]
