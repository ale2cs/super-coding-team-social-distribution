# Generated by Django 4.2.6 on 2023-11-26 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0004_friendfollowrequest_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowerRemote',
            fields=[
                ('id', models.CharField(max_length=300, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='follower',
            name='followingRemote',
            field=models.ManyToManyField(blank=True, related_name='followed_by', to='author.followerremote'),
        ),
    ]
