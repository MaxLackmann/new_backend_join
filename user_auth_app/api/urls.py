from django.urls import path
from .views import CustomerUserList, CustomerUserDetail, RegisterView, EmailLoginView

urlpatterns = [
    path('users/', CustomerUserList.as_view(), name='customeruser-list'),
    path('users/<int:pk>/', CustomerUserDetail.as_view(), name='customeruserdetail-detail'),
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', EmailLoginView.as_view(), name='login'),
]
