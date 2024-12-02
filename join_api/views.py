from django.shortcuts import render
from rest_framework import generics
from .serializers import ContactSerializer, TaskSerializer, SubtaskSerializer #, UserSerializer
from .models import Contact,Task, Subtask #,User



class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
class SubtaskList(generics.ListCreateAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    
class SubtaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
