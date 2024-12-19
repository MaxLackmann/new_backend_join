from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ContactSerializer, TaskSerializer, SubtaskSerializer
from ..models import Contact, Task, Subtask

class ContactList(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        contacts = Contact.objects.filter(user=user)

        # Benutzer selbst hinzufügen, wenn nicht vorhanden
        if not contacts.filter(email=user.email).exists():
            Contact.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                emblem=user.emblem,
                color=user.color,
                phone="123456789",

            )
        return contacts

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'cardId'

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)

class SubtaskList(generics.ListCreateAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task = self._get_task()
        return Subtask.objects.filter(task=task)

    def perform_create(self, serializer):
        task = self._get_task()
        serializer.save(task=task)

    def _get_task(self):
        task_id = self.kwargs.get('cardId')
        return get_object_or_404(Task, cardId=task_id, created_by=self.request.user)

class SubtaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        task = self._get_task()
        subtask = self._get_subtask(task)
        serializer = self.serializer_class(subtask, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_task(self):
        task_id = self.kwargs.get('cardId')
        return get_object_or_404(Task, cardId=task_id, created_by=self.request.user)

    def _get_subtask(self, task):
        subtask_id = self.kwargs.get('id')
        return get_object_or_404(Subtask, id=subtask_id, task=task)
