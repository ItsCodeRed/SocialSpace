# Generated by Django 4.0.4 on 2022-07-06 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_followercount'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follower_count',
            field=models.IntegerField(default=0),
        ),
    ]
