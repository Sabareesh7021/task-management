from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginAPIView.as_view(), name='login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
    path('users/',views.UserAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserAPIView.as_view(), name='user-detail'),
]