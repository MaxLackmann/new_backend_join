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
        if len(value) > 5: 
            raise serializers.ValidationError("Es sind maximal 5 Subtasks erlaubt.")
        return value
        
class TaskSerializer(serializers.ModelSerializer):
    contact_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Contact.objects.all(), source='contacts')
    contacts = ContactSerializer(many=True, read_only=True)
    subtasks = SubtaskSerializer(many=True)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'contact_ids', 'contacts', 'subtasks')

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        contacts_data = validated_data.pop('contacts', [])

        task = Task.objects.create(**validated_data)

        task.contacts.set(contacts_data)
        for contact in contacts_data:
            contact.checked = True
            contact.save()

        self._create_subtasks(task, subtasks_data)

        return task

    def update(self, instance, validated_data):
        self._classic_update(instance, validated_data)
        
        existing_contacts = set(instance.contacts.all())
        new_contacts_data = validated_data.pop('contacts', [])
        
        self._removechecked(existing_contacts, new_contacts_data)

        instance.contacts.set(new_contacts_data)
        self._setchecked(new_contacts_data)

        subtasks_data = validated_data.pop('subtasks', [])
        self._update_subtasks(instance, subtasks_data)

        instance.save()

        return instance
    
    def _classic_update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.date = validated_data.get('date', instance.date)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.category = validated_data.get('category', instance.category)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
    
    def _removechecked(self, existing_contacts, new_contacts_data):
        for contact in existing_contacts:
            if contact not in new_contacts_data:
                contact.checked = False
                contact.save()
        
    def _setchecked(self, new_contacts_data):
        for contact in new_contacts_data:
            contact.checked = True
            contact.save()

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