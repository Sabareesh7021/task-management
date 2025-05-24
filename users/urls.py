from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginAPIView.as_view(), name='login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
    path('get-users/',views.UserAPIView.as_view(), name='user-list'),
    path('create-user/',views.UserAPIView.as_view(), name='user-create'),
    path('update-user/<int:pk>/',views.UserAPIView.as_view(), name='user-update'),
    path('user/<int:pk>/', views.UserAPIView.as_view(), name='user-user-by-id'),
    path('delete-user/<int:pk>/', views.UserAPIView.as_view(), name='user-delete'),
]

