# Generated by Django 4.2.6 on 2023-11-27 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inbox", "0008_remoteinbox_requests"),
    ]

    operations = [
        migrations.RenameField(
            model_name="remoteinboxitem",
            old_name="id_url",
            new_name="object_url",
        ),
        migrations.AddField(
            model_name="remoteinboxitem",
            name="remote_author",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
    ]
