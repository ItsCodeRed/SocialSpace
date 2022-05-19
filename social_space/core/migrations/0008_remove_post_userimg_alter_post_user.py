# Generated by Django 4.0.4 on 2022-05-18 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_post_userimg'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='userimg',
        ),
        migrations.AlterField(
            model_name='post',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.profile'),
        ),
    ]
