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
    contacts = ContactSerializer(many=True)
    subtasks = SubtaskSerializer(many=True)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'contacts', 'subtasks')

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        contacts_data = validated_data.pop('contacts', [])

        # Erstelle den Task
        task = Task.objects.create(**validated_data)

        # Füge die Kontakte hinzu
        self._create_or_update_contacts(task, contacts_data)
        self._create_subtasks(task, subtasks_data)

        return task

    def update(self, instance, validated_data):
        # Aktualisiere die Felder des Tasks
        self._update_task_fields(instance, validated_data)

        # Extrahiere die Kontakte und Subtasks
        contacts_data = validated_data.pop('contacts', [])
        subtasks_data = validated_data.pop('subtasks', [])

        # Kontakte und Subtasks aktualisieren
        self._create_or_update_contacts(instance, contacts_data)
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
        """
        Erstellt oder aktualisiert Kontakte und fügt sie einem Task hinzu, ohne Duplikate zu erzeugen.
        """
        # IDs der aktuell verknüpften Kontakte (bereits in der Datenbank)
        existing_contact_ids = set(task.contacts.values_list('id', flat=True))
        received_contact_ids = set()
    
        for contact_data in contacts_data:
            contact_id = contact_data.get('id')
    
            # Debug-Ausgabe zur Überprüfung des aktuellen Kontakts
            print(f"Verarbeiteter Kontakt: {contact_data}, Extrahierte ID: {contact_id}")
    
            if contact_id:
                # Kontakt mit gegebener ID bearbeiten und hinzufügen
                try:
                    contact = Contact.objects.get(id=contact_id)
                    contact.name = contact_data.get('name', contact.name)
                    contact.email = contact_data.get('email', contact.email)
                    contact.phone = contact_data.get('phone', contact.phone)
                    contact.emblem = contact_data.get('emblem', contact.emblem)
                    contact.color = contact_data.get('color', contact.color)
                    contact.checked = contact_data.get('checked', contact.checked)
                    contact.save()
                    task.contacts.add(contact)
                    received_contact_ids.add(contact_id)
                    print(f"Kontakt mit ID {contact_id} wurde aktualisiert und zum Task hinzugefügt.")
                except Contact.DoesNotExist:
                    raise serializers.ValidationError(f"Contact with ID {contact_id} does not exist.")
    
            else:
                # Wenn keine ID vorhanden ist, prüfen, ob der Kontakt bereits existiert (z.B. anhand von `email`)
                email = contact_data.get('email')
                if email:
                    # Suchen nach einem bestehenden Kontakt mit derselben Email
                    try:
                        contact = Contact.objects.get(email=email)
                        # Wenn gefunden, aktualisieren und zum Task hinzufügen
                        contact.name = contact_data.get('name', contact.name)
                        contact.phone = contact_data.get('phone', contact.phone)
                        contact.emblem = contact_data.get('emblem', contact.emblem)
                        contact.color = contact_data.get('color', contact.color)
                        contact.checked = contact_data.get('checked', contact.checked)
                        contact.save()
                        task.contacts.add(contact)
                        received_contact_ids.add(contact.id)
                        print(f"Bestehender Kontakt mit Email {email} wurde aktualisiert und zum Task hinzugefügt.")
                    except Contact.DoesNotExist:
                        # Wenn der Kontakt nicht existiert, erstelle ihn neu
                        new_contact = Contact.objects.create(**contact_data)
                        task.contacts.add(new_contact)
                        received_contact_ids.add(new_contact.id)
                        print(f"Neuer Kontakt wurde erstellt und zum Task hinzugefügt: {new_contact}")
    
        # Kontakte entfernen, die nicht mehr in den übergebenen Daten enthalten sind
        contacts_to_remove = existing_contact_ids - received_contact_ids
        for contact_id in contacts_to_remove:
            contact = Contact.objects.get(id=contact_id)
            task.contacts.remove(contact)
            print(f"Kontakt mit ID {contact_id} wurde vom Task entfernt.")
    
        # Änderungen speichern
        task.save()
        print(f"Nach der Aktualisierung der Kontakte: {task.contacts.all()}")
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

        # Entferne Subtasks, die nicht mehr in der neuen Liste enthalten sind
        for subtask_id in existing_subtask_ids - received_subtask_ids:
            Subtask.objects.filter(id=subtask_id).delete()