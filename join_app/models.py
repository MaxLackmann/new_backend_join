from django.db import models
from user_auth_app.models import CustomUser
from django.core.exceptions import ValidationError
from user_auth_app.api.validators import validate_username_format, validate_phone_format


class Contact(models.Model):
    name = models.CharField(max_length=50, validators=[validate_username_format])
    email = models.EmailField(
        max_length=254,
        error_messages={
            "email": "Enter a valid email address"
        }
    )
    phone = models.CharField(
        max_length=13,
        validators=[validate_phone_format],
    )
    emblem = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts')

    def clean(self):

        if Contact.objects.filter(user=self.user, email=self.email).exclude(id=self.id).exists():
            raise ValidationError("email already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
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