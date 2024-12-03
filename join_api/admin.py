from django.contrib import admin
from .models import Contact, User, Task, Subtask

class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 1 

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'emblem', 'color', 'checked')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'password', 'confirm_password', 'emblem', 'color')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'contacts', 'subtasks')
    inlines = [SubtaskInline]

    def contacts(self, obj):
        return ", ".join([contact.name for contact in obj.contacts.all()])
    
    def subtasks(self, obj):
        return ", ".join([subtask.subtasktext for subtask in obj.subtasks.all()])

@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('subtasktext', 'checked', 'task')