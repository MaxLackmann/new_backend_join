from rest_framework import serializers
from ..models import Contact, Task, Subtask, TaskUserDetails
from user_auth_app.models import CustomUser
from user_auth_app.api.serializers import CustomUserSerializer

class ContactSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False)
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'phone', 'emblem', 'color')

    def create(self, validated_data):
        user = self.context['request'].user

        # Sicherstellen, dass der Benutzer selbst in der Liste ist
        if not Contact.objects.filter(user=user, email=user.email).exists():
            Contact.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                emblem=user.emblem,
                color=user.color,
                phone=user.phone,
            )

        # Zusätzliche Kontakte hinzufügen
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Normales Update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Synchronisiere die Benutzerdaten mit `CustomUser`
        user = self.context['request'].user
        if 'name' in validated_data:
            user.username = validated_data['name']
        if 'email' in validated_data:
            user.email = validated_data['email']
        if 'emblem' in validated_data:
            user.emblem = validated_data['emblem']
        if 'color' in validated_data:
            user.color = validated_data['color']
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        
        user.save()

        return instance
    
    def perform_destroy(self, instance):
        user = instance.user
        
        # Lösche zuerst den Kontakt
        instance.delete()

        # Lösche auch den Benutzer, wenn er der aktuelle Benutzer ist
        if user == self.request.user:
            user.delete()

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
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    user = TaskUserDetailsSerializer(source='user_statuses', many=True, read_only=True)
    subtasks = SubtaskSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'user_ids', 'user', 'subtasks')

    def validate_user_ids(self, user_ids):
        for user_id in user_ids:
            if not CustomUser.objects.filter(id=user_id).exists():
                raise serializers.ValidationError(f"Invalid user ID: {user_id}")
        return user_ids

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        user_ids = validated_data.pop('user_ids', [])

        task = Task.objects.create(**validated_data)
        self._assign_task_users(task, user_ids)
        self._assign_subtasks(task, subtasks_data)

        return task

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        user_ids = validated_data.pop('user_ids', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._assign_task_users(instance, user_ids)
        self._assign_subtasks(instance, subtasks_data)

        return instance

    def _assign_task_users(self, task, user_ids):
        task.user.clear()
        TaskUserDetails.objects.bulk_create([
            TaskUserDetails(task=task, user_id=user_id, checked=True) for user_id in user_ids
        ])

    def _assign_subtasks(self, task, subtasks_data):
        Subtask.objects.filter(task=task).delete()
        Subtask.objects.bulk_create([
            Subtask(task=task, **subtask_data) for subtask_data in subtasks_data
        ])
