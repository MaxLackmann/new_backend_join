from django.contrib import admin
from .models import Contact, User, Task, Subtask

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'emblem', 'color', 'checked')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password', 'confirm_password', 'emblem', 'color')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'contacts')

    def contacts(self, obj):
        return ", ".join([contact.name for contact in obj.contacts.all()])

@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('subtasktext', 'checked', 'task')