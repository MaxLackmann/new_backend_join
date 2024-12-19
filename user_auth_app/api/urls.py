from django.urls import path
from join_app.api.views import ContactList, ContactDetail, TaskList, TaskDetail, SubtaskList, SubtaskDetail
from .views import CustomerUserList, CustomerUserDetail, RegisterView, EmailLoginView

urlpatterns = [
    # Benutzerverwaltung
    path('users/', CustomerUserList.as_view(), name='customeruser-list'),
    path('users/<int:pk>/', CustomerUserDetail.as_view(), name='customeruser-detail'),

    # Registrierung und Login
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', EmailLoginView.as_view(), name='login'),

    # Tasks (keine Benutzer-ID notwendig)
    path('tasks/', TaskList.as_view(), name='task-list'),
    path('tasks/<int:cardId>/', TaskDetail.as_view(), name='task-detail'),

    # Subtasks (Task-ID notwendig)
    path('tasks/<int:cardId>/subtasks/', SubtaskList.as_view(), name='task-subtask-list'),
    path('tasks/<int:cardId>/subtasks/<int:id>/', SubtaskDetail.as_view(), name='task-subtask-detail'),

    # Kontakte (keine Benutzer-ID notwendig)
    path('contacts/', ContactList.as_view(), name='contact-list'),
    path('contacts/<int:id>/', ContactDetail.as_view(), name='contact-detail'),
]