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

    def create(self, validated_data):
        # Verwende Hilfsfunktionen für das Erstellen
        subtasks_data = validated_data.pop('subtasks', [])
        contacts_data = validated_data.pop('contacts', [])

        task = Task.objects.create(**validated_data)

        # Erstelle Kontakte und Subtasks
        self._create_or_update_contacts(task, contacts_data)
        self._create_subtasks(task, subtasks_data)

        return task
    
    def update(self, instance, validated_data):
        self._update_task_fields(instance, validated_data)

        contacts_data = validated_data.pop('contacts', [])
        subtasks_data = validated_data.pop('subtasks', [])

        if contacts_data:
            self._update_contacts(instance, contacts_data)

        if subtasks_data:
            self._update_subtasks(instance, subtasks_data)

        return instance

    # Helper Functions
    def _update_task_fields(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.date = validated_data.get('date', instance.date)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.category = validated_data.get('category', instance.category)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

    def _create_or_update_contacts(self, task, contacts_data):
        for contact_data in contacts_data:
            contact = Contact.objects.get(id=contact_data['id'])
            contact.checked = bool(contact_data.get('checked', False))  # Checked aktualisieren
            contact.save()
            if contact.checked:
                task.contacts.add(contact)

    def _update_contacts(self, instance, contacts_data):
        existing_contacts = {contact.id: contact for contact in instance.contacts.all()}  # Aktuelle Kontakte im Task
        new_contacts_data = []

        for contact_data in contacts_data:
            contact_id = contact_data.get('id')
            if contact_id and contact_id in existing_contacts:
                contact = existing_contacts.pop(contact_id)
                contact.name = contact_data.get('name', contact.name)
                contact.email = contact_data.get('email', contact.email)
                contact.phone = contact_data.get('phone', contact.phone)
                contact.emblem = contact_data.get('emblem', contact.emblem)
                contact.color = contact_data.get('color', contact.color)
                contact.checked = contact_data.get('checked', contact.checked)
                contact.save()
            else:
                new_contacts_data.append(contact_data)

        for contact_data in new_contacts_data:
            contact = Contact.objects.create(**contact_data)
            instance.contacts.add(contact)

        for contact_id in existing_contacts:
            instance.contacts.remove(existing_contacts[contact_id])

    def _create_subtasks(self, task, subtasks_data):
        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)

    def _update_subtasks(self, instance, subtasks_data):
        existing_subtask_ids = set(instance.subtasks.values_list('id', flat=True))
        received_subtask_ids = set()

        for subtask_data in subtasks_data:
            subtask_id = subtask_data.get('id')
            if subtask_id and subtask_id in existing_subtask_ids:
                subtask = Subtask.objects.get(id=subtask_id, task=instance)
                subtask.subtasktext = subtask_data.get('subtasktext', subtask.subtasktext)
                subtask.checked = subtask_data.get('checked', subtask.checked)
                subtask.save()
                received_subtask_ids.add(subtask_id)
            else:
                new_subtask = Subtask.objects.create(task=instance, **subtask_data)
                received_subtask_ids.add(new_subtask.id)

        for subtask_id in existing_subtask_ids - received_subtask_ids:
            Subtask.objects.filter(id=subtask_id).delete()