# Generated by Django 4.2.6 on 2023-11-24 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0009_liked'),
        ('inbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='comment_likes',
            field=models.ManyToManyField(blank=True, related_name='rec_comment_likes', to='post.commentlike'),
        ),
    ]