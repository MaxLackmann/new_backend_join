# Generated by Django 5.1.3 on 2024-12-09 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('join_app', '0004_alter_contact_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
