# Generated by Django 4.2.6 on 2023-11-25 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0002_friendfollowrequest_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendfollowrequest',
            name='status',
        ),
    ]