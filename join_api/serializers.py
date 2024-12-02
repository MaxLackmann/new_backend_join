from rest_framework import serializers
from .models import Contact, User, Task, Subtask

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'phone', 'emblem', 'color', 'checked')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'confirm_password', 'emblem', 'color')
        
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'contacts') 
        
class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ('id', 'subtasktext', 'checked', 'task')