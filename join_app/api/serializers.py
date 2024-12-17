from rest_framework import serializers
from ..models import Contact, Task, Subtask, TaskUserDetails #ContactUserDetails
from user_auth_app.models import CustomUser
from user_auth_app.api.serializers import CustomUserSerializer

class ContactSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'phone', 'emblem', 'color')

    def create(self, validated_data):
        user = self.context['request'].user
        if not Contact.objects.filter(user=user, email=user.email).exists():
            Contact.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                phone="",  # oder andere Standardwerte
                emblem=user.emblem,
                color=user.color,
            )
        return super().create(validated_data)

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ('id', 'subtasktext', 'checked', 'task')
        read_only_fields = ('task',)
        
    def validate_subtasks(self, value):
        if len(value) > 5: 
            raise serializers.ValidationError("Es sind maximal 5 Subtasks erlaubt.")
        return value
    
class TaskUserDetailsSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = TaskUserDetails
        fields = ('user', 'checked')
        
class TaskSerializer(serializers.ModelSerializer):
    user_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        required=False,
        source='user'
    )
    user = TaskUserDetailsSerializer(source='user_statuses', many=True, read_only=True)
    subtasks = SubtaskSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'user_ids', 'user', 'subtasks')

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        user_ids = validated_data.pop('user', [])

        # Task erstellen
        task = Task.objects.create(**validated_data)

        # Benutzer in die Zwischentabelle eintragen
        for user in user_ids:
            TaskUserDetails.objects.create(task=task, user=user, checked=True)

        # Subtasks erstellen
        self._create_subtasks(task, subtasks_data)

        return task

    def update(self, instance, validated_data):
        user_ids = validated_data.pop('user', [])
        subtasks_data = validated_data.pop('subtasks', [])

        # Aktualisiere Task selbst
        self._classic_update(instance, validated_data)

        # Benutzer aktualisieren
        instance.user.clear()
        for user in user_ids:
            TaskUserDetails.objects.update_or_create(
                task=instance, user=user,
                defaults={"checked": True}
            )

        # Subtasks aktualisieren
        self._update_subtasks(instance, subtasks_data)

        return instance

    def _classic_update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.date = validated_data.get('date', instance.date)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.category = validated_data.get('category', instance.category)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

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
                Subtask.objects.create(task=instance, **subtask_data)
                received_subtask_ids.add(subtask_id)

        for subtask_id in existing_subtask_ids - received_subtask_ids:
            Subtask.objects.filter(id=subtask_id).delete()