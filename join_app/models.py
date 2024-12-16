from django.db import models
from user_auth_app.models import CustomUser
from django.core.exceptions import ValidationError

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.TextField()
    emblem = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts')

    def save(self, *args, **kwargs):
        if not self.id and Contact.objects.filter(user=self.user, email=self.email).exists():
            raise ValidationError("Der Benutzer ist bereits als Kontakt vorhanden.")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class ContactUserDetails(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='user_details')
    phone = models.TextField(blank=True)

    def __str__(self):
        return f"Contact: {self.contact.name}, User: {self.user.username}, Phone: {self.phone}"
    
class Task(models.Model):
    cardId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    priority = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    user = models.ManyToManyField(CustomUser, blank=True, related_name='tasks')    
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