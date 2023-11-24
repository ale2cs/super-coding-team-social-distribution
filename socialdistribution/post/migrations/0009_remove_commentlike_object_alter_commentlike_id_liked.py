# Generated by Django 4.2.6 on 2023-11-24 03:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("post", "0008_merge_0005_alter_post_id_0007_commentlike"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="commentlike",
            name="object",
        ),
        migrations.AlterField(
            model_name="commentlike",
            name="id",
            field=models.CharField(
                default=uuid.uuid4,
                editable=False,
                max_length=200,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.CreateModel(
            name="Liked",
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
                (
                    "likedPosts",
                    models.ManyToManyField(
                        blank=True, related_name="liked_posts", to="post.like"
                    ),
                ),
            ],
        ),
    ]