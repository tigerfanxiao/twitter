# Generated by Django 4.1.2 on 2022-10-23 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("friendships", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="friendship",
            options={"ordering": ("-created_at",)},
        ),
    ]
