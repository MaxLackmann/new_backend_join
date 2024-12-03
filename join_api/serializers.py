from rest_framework import serializers
from .models import Contact, User, Task, Subtask

class ContactSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'phone', 'emblem', 'color', 'checked')
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'confirm_password', 'emblem', 'color')
        
class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ('id', 'subtasktext', 'checked', 'task')
        read_only_fields = ('task',)
        
    def validate_subtasks(self, value):
        if len(value) > 5:  # Maximal 5 Subtasks erlauben
            raise serializers.ValidationError("Es sind maximal 5 Subtasks erlaubt.")
        return value
        
class TaskSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True)
    subtasks = SubtaskSerializer(many=True)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'contacts', 'subtasks')

    def validate_contacts(self, value):
        for contact in value:
            if 'id' not in contact:
                raise serializers.ValidationError(f"Kontakt ohne 'id': {contact}")
        return value

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', validated_data.pop('subtask', []))
        contacts_data = validated_data.pop('contacts', [])

        # Task erstellen
        task = Task.objects.create(**validated_data)

        # Kontakte verarbeiten und mit Task verknüpfen
        for contact_data in contacts_data:
            contact = Contact.objects.get(id=contact_data['id'])
            contact.checked = bool(contact_data.get('checked', False))  # Checked aktualisieren
            contact.save()
            if contact.checked:
                task.contacts.add(contact)

        # Subtasks erstellen
        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)

        return task