from rest_framework import serializers
from ..models import Contact, Task, Subtask, ContactUserDetails, TaskUserDetails
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
        
class TaskSerializer(serializers.ModelSerializer):
    username_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all(), source='users')
    usernames = CustomUserSerializer(many=True, read_only=True)
    subtasks = SubtaskSerializer(many=True)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'username_ids', 'usernames', 'subtasks')

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        usernames_data   = validated_data.pop('usernames', [])

        task = Task.objects.create(**validated_data)

        task.users.set(usernames_data )
        for user in usernames_data :
            user.checked = True
            user.save()

        self._create_subtasks(task, subtasks_data)

        return task

    def update(self, instance, validated_data):
        self._classic_update(instance, validated_data)
        
        existing_usernames = set(instance.usernames.all())
        new_usernames_data = validated_data.pop('usernames', [])
        
        self._removechecked(existing_usernames, new_usernames_data)

        instance.username.set(new_usernames_data)
        self._setchecked(new_usernames_data, instance) # das instance kommt von chatgpt


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
    
    def _removechecked(self, existing_usernames, new_usernames_data):
        for user in existing_usernames:
            if user not in new_usernames_data:
                user.checked = False
                user.save()
        
    def _setchecked(self, new_usernames_data):
        for user in new_usernames_data:
            user.checked = True
            user.save()

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