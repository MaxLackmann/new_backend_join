from rest_framework import serializers
from ..models import Contact, Task, Subtask, TaskUserDetails
from user_auth_app.models import CustomUser
from user_auth_app.api.serializers import CustomUserSerializer
import re

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'phone', 'emblem', 'color')
        read_only_fields = ('id',)

    def validate_email(self, value):
        """
        Validiert die E-Mail eines Kontakts:
        - Sie darf nicht die gleiche E-Mail wie die des aktuellen Benutzers sein.
        - Sie darf nicht bereits einem anderen Kontakt desselben Benutzers gehören.
        - Sie darf nicht bereits einem anderen Benutzer gehören.
        """
        user = self.context['request'].user
        contact_id = self.instance.id if self.instance else None

        # 🔹 1. E-Mail darf nicht die des Benutzers sein
        if user.email == value:
            raise serializers.ValidationError("E-Mail cannot be the same as the user's E-Mail.")

        # 🔹 2. E-Mail darf nicht einem anderen Kontakt des Benutzers gehören
        if Contact.objects.filter(user=user, email=value).exclude(id=contact_id).exists():
            raise serializers.ValidationError("This email is already associated with another contact of yours.")

        # 🔹 3. E-Mail darf nicht einem anderen Benutzer gehören
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already associated with a user account.")

        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    
    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()

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