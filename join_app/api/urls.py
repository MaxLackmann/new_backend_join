# from django.urls import path
# from .views import ContactList, ContactDetail, TaskList, TaskDetail, SubtaskList, SubtaskDetail

# urlpatterns = [
#     path('contacts/', ContactList.as_view()),
#     path('contacts/<int:pk>/', ContactDetail.as_view()),
#     path('tasks/', TaskList.as_view()),
#     path('tasks/<int:pk>/', TaskDetail.as_view()),
#     path('subtasks/', SubtaskList.as_view()),
#     path('subtasks/<int:pk>/', SubtaskDetail.as_view()),
#     path('tasks/<int:task_id>/subtasks/<int:subtask_id>/', SubtaskDetail.as_view(), name='task-subtask-detail'),
# ]