# Generated by Django 4.2.6 on 2023-12-02 22:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("post", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="remotecomment",
            name="author",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="remotecomment",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="post.post"
            ),
        ),
        migrations.AlterField(
            model_name="remotelike",
            name="author",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="remotelike",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="post.post"
            ),
        ),
    ]
