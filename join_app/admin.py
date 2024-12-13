from django.contrib import admin
from .models import Contact, Task, Subtask, TaskUser, UserContact

class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 1 

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'emblem', 'color')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'display_users', 'display_subtasks')
    inlines = [SubtaskInline]

    def display_users(self, obj):
        # Gibt eine kommagetrennte Liste der Nutzer zurück
        return ", ".join([user.username for user in obj.users.all()])
    display_users.short_description = "Users"

    def display_subtasks(self, obj):
        # Gibt eine kommagetrennte Liste der Subtasks zurück
        return ", ".join([subtask.subtasktext for subtask in obj.subtasks.all()])
    display_subtasks.short_description = "Subtasks"

@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('subtasktext', 'checked', 'task')

@admin.register(TaskUser)
class TaskUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'task', 'checked')

@admin.register(UserContact)
class UserContactAdmin(admin.ModelAdmin):
    list_display = ('username', 'contact', 'phone')