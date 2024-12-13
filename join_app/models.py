from django.db import models
from user_auth_app.models import CustomUser

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.TextField()
    emblem = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts'
                             , null=True, blank=True)
    
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
    username = models.ManyToManyField(CustomUser, blank=True, related_name='tasks')    
    def __str__(self):
        return self.title

class Subtask(models.Model):
    subtasktext = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    
    def __str__(self):
        return f"{self.subtasktext} (Checked: {self.checked})"

class TaskUser(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)

    
    def __str__(self):
        return f"{self.username} - {self.task}"
    
class UserContact(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} - {self.contact}"
