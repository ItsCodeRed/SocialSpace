# Generated by Django 4.0.4 on 2022-05-18 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_user_post_user_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='user_profile',
        ),
    ]
