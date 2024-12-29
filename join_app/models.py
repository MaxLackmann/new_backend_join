from django.db import models
from user_auth_app.models import CustomUser
from django.core.exceptions import ValidationError
import re


def validate_email_format(value):
    """
    Stellt sicher, dass die E-Mail eine gültige Struktur und TLD besitzt.
    """
    email_regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError("Die E-Mail-Adresse muss eine gültige Top-Level-Domain (z.B. .de, .com, .net) haben.")

def validate_phone_format(value):
    phone_regex = r'^\+?[0-9\s\-]{6,13}$'
    if not re.match(phone_regex, value):
        raise ValidationError("Die Telefonnummer muss zwischen 6 und 13 Zeichen lang sein und darf nur Ziffern, Leerzeichen, Bindestriche oder ein '+' enthalten.")

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(validators=[validate_email_format])
    phone = models.CharField(max_length=13, validators=[validate_phone_format])
    emblem = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts')

    def clean(self):
        """
        Überprüft, ob die E-Mail bereits in der Kontaktliste des Benutzers existiert.
        """
        if Contact.objects.filter(user=self.user, email=self.email).exclude(id=self.id).exists():
            raise ValidationError("Diese E-Mail existiert bereits in Ihrer Kontaktliste.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Task(models.Model):
    cardId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    priority = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='created_tasks'
    )  
    user = models.ManyToManyField(
        CustomUser, 
        through='TaskUserDetails',
        related_name='tasks'
    )

    def __str__(self):
        return self.title
    
class TaskUserDetails(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='user_statuses')
    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"Task: {self.task.title}, User: {self.user.username}, Checked: {self.checked}"

class Subtask(models.Model):
    subtasktext = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    
    def __str__(self):
        return f"{self.subtasktext} (Checked: {self.checked})"