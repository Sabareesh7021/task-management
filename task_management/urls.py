from django.urls import path
from . import views

urlpatterns = [
    path('get-tasks/', views.TaskAPIView.as_view(), name='task-lists'),
    path('get-task/<int:pk>/', views.TaskAPIView.as_view(), name='task-'),
    path('create-task/', views.TaskAPIView.as_view(), name='task-create'),
    path('update-task/<int:pk>/', views.TaskAPIView.as_view(), name='task-update'),
    path('delete-task/<int:pk>/', views.TaskAPIView.as_view(), name='task-delete'),
    path('start-task/<int:pk>/', views.TaskManagementAPIView.as_view(), name='task-start'),
]