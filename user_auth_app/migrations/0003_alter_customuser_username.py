# Generated by Django 5.1.3 on 2024-12-13 20:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0002_create_guest_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(code='invalid', message='Benutzername darf Buchstaben, Zahlen, Leerzeichen und @/./+/-/_ enthalten.', regex='^[a-zA-Z0-9@.+\\\\-_\\\\s]+$')]),
        ),
    ]
