from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

def validate_username(value):
    if not all(c.isalnum() or c in " ._- " for c in value):  # Erlaubte Zeichen prüfen
        raise ValidationError(
            'Benutzername darf nur Buchstaben, Zahlen, Leerzeichen und @/./+/-/_ enthalten.',
            code='invalid'
        )

class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username],
        help_text='150 Zeichen oder weniger. Buchstaben, Zahlen, Leerzeichen und @/./+/-/_ erlaubt.',
    )
    email = models.EmailField(unique=True)
    emblem = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if self.username == "guest":
            self.set_unusable_password()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email