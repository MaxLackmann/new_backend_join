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

    # Benutzer-spezifische Tasks
    path('users/<int:pk>/tasks/', TaskList.as_view(), name='user-task-list'),
    path('users/<int:pk>/tasks/<int:task_id>/', TaskDetail.as_view(), name='user-task-detail'),

    # Benutzer-spezifische Subtasks
    path('users/<int:pk>/tasks/<int:task_id>/subtasks/', SubtaskList.as_view(), name='user-task-subtask-list'),
    path('users/<int:pk>/tasks/<int:task_id>/subtasks/<int:subtask_id>/', SubtaskDetail.as_view(), name='user-task-subtask-detail'),

    # Benutzer-spezifische Kontakte
    path('users/<int:pk>/contacts/', ContactList.as_view(), name='user-contact-list'),
    path('users/<int:pk>/contacts/<int:contact_id>/', ContactDetail.as_view(), name='user-contact-detail'),

]