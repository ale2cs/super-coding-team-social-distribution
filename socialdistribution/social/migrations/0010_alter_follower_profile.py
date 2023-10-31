# Generated by Django 4.2.6 on 2023-10-29 17:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0009_likes_liked"),
    ]

    operations = [
        migrations.AlterField(
            model_name="follower",
            name="profile",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="profile",
                to="social.profile",
            ),
        ),
    ]
