# Generated by Django 5.1.3 on 2024-12-13 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('join_app', '0007_contact_user_task_users_taskusers_task_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='user',
            new_name='username',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='users',
            new_name='username',
        ),
        migrations.RenameField(
            model_name='taskusers',
            old_name='user',
            new_name='username',
        ),
        migrations.RenameField(
            model_name='usercontacts',
            old_name='user',
            new_name='username',
        ),
    ]
