from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ContactSerializer, TaskSerializer, SubtaskSerializer 
from ..models import Contact,Task, Subtask, TaskUserDetails, ContactUserDetails

class ContactList(generics.ListCreateAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        user = self.request.user
        # Prüfen, ob der Benutzer sich selbst als Kontakt hat
        if not Contact.objects.filter(user=user, email=user.email).exists():
            Contact.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                phone="",  # oder andere Standardwerte
                emblem=user.emblem,
                color=user.color,
            )
        # Kontakte des aktuellen Benutzers abrufen
        return Contact.objects.filter(user=user)

    
class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        # Nur Kontakte des aktuellen Benutzers abrufen
        return Contact.objects.filter(user=self.request.user)

class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        """
        Filter Tasks so, dass nur Tasks zurückgegeben werden,
        die dem eingeloggten Benutzer zugeordnet sind.
        """
        return Task.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        # Nur Tasks des aktuellen Benutzers abrufen
        return Task.objects.filter(user=self.request.user)
    
class SubtaskList(generics.ListCreateAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    def get_queryset(self):
        # Subtasks nur für Tasks des aktuellen Benutzers abrufen
        return Subtask.objects.filter(task__user=self.request.user)
    
class SubtaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    
    def get_queryset(self):
        # Subtasks nur für Tasks des aktuellen Benutzers abrufen
        return Subtask.objects.filter(task__user=self.request.user)

    def patch(self, request, *args, **kwargs):
        task_id = kwargs.get('task_id')
        subtask_id = kwargs.get('subtask_id')

        task = get_object_or_404(Task, id=task_id, user=self.request.user)
        subtask = get_object_or_404(Subtask, id=subtask_id, task=task)

        serializer = self.serializer_class(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
