# Generated by Django 4.2.6 on 2023-11-27 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inbox", "0010_remove_remoteinbox_items_delete_remoteinboxitem_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="remoteinbox",
            name="items",
            field=models.JSONField(default=[]),
        ),
    ]
