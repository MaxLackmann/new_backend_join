from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.TextField()
    emblem = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
class Task(models.Model):
    cardId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    priority = models.IntegerField()
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    contacts = models.ManyToManyField(Contact, blank=True)
    
    def __str__(self):
        return self.title

class Subtask(models.Model):
    subtasktext = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.subtasktext & self.checked
    
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
    emblem = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)