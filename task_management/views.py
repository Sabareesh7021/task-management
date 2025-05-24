from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (status, permissions)
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Task
from utils.common import BaseAPIView
from utils.pagination import paginate
from .serializer import TaskSerializer


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class TaskAPIView(BaseAPIView):
    def get_permissions(self):
        method = self.request.method
        if method == 'GET':
            return [IsAuthenticated()]
        elif method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        elif method == 'PATCH':
            return [IsAuthenticated()]
        elif method == 'DELETE':
            return [IsAuthenticated(), IsSuperAdmin()]
        return super().get_permissions()
    
    def get_object(self, pk):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=pk)
    

    def get_queryset(self):
        user = self.request.user
        status_param = self.request.query_params.get('status')
        assigned_to  = self.request.query_params.get('assignedTo')
        search       = self.request.query_params.get('search')

        queryset = Task.objects.all() if user.is_superuser else (
            Task.objects.filter(Q(assigned_to=user) | Q(assigned_by=user)) if user.is_staff else
            Task.objects.filter(assigned_to=user)
        )

        if status_param:
            queryset = queryset.filter(status=status_param)
        if assigned_to:
            queryset = queryset.filter(assigned_to__id=assigned_to)
        if search:
            queryset = queryset.filter(
                    Q(description__icontains=search) | Q(title__icontains=search)
                )
        return queryset


    def get(self, request, pk=None):
        try:
            if pk:
                task = self.commonUtils.get_object(pk)
                serializer = TaskSerializer(task)
                return self._format_response(True, "Task retrieved successfully", serializer.data)

            tasks = self.get_queryset()
            paginated_data = paginate(tasks, request)
            serializer = TaskSerializer(paginated_data['data'], many=True)

            return self._format_response(
                True,
                "Tasks list retrieved successfully",
                serializer.data,
                status_code=status.HTTP_200_OK,
                pagination=paginated_data
            )
        except Exception as e:
            return self._format_response(False, str(e), None, status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            serializer = TaskSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(assigned_by=request.user)

            return self._format_response(
                True,
                "Task created successfully",
                serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return self._format_response(False, str(e), None, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            task = self.get_object(pk)
            if request.data is None:
                return self._format_response(
                    False, 
                    "No data provided for update", 
                    None, 
                    status.HTTP_400_BAD_REQUEST
                )
            self._validate_user_update_permissions(request.user, task, request.data)

            serializer = TaskSerializer(
                task,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return self._format_response(
                True,
                "Task updated successfully",
                serializer.data
            )
        except PermissionDenied as e:
            return self._format_response(False, str(e), None, status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return self._format_response(False, str(e), None, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = self.get_object(pk)
            task.delete()
            return self._format_response(
                True,
                "Task deleted successfully",
                None,
                status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return self._format_response(False, str(e), None, status.HTTP_400_BAD_REQUEST)

    def _validate_user_update_permissions(self, user, task, data):
        if user.is_staff or user.is_superuser:
            return
        
        if task.assigned_to != user:
            raise PermissionDenied("You can only update tasks assigned to you")
        

class TaskManagementAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        """
        Handle POST request to start a task
        """
        try:
            task = Task.objects.get(pk=pk)
            if task.assigned_to != request.user:
                return self._format_response(
                    False,
                    "You can only start tasks assigned to you",
                    None,
                    status.HTTP_403_FORBIDDEN
                )
            
            if task.status != 'pending':
                return self._format_response(
                    False,
                    f"Task cannot be started from {task.status} status",
                    None,
                    status.HTTP_400_BAD_REQUEST
                )
        
            active_tasks = Task.objects.filter(
                assigned_to=request.user,
                status='in_progress'
            ).exclude(id=task.id)
            
            if active_tasks.exists():
                return self._format_response(
                    False,
                    "You can only work on one task at a time. "
                    "Please complete your current task before starting a new one.",
                    None,
                    status.HTTP_400_BAD_REQUEST
                )
            
            task.status = 'in_progress'
            task.save()
            
            serializer = TaskSerializer(task)
            return self._format_response(
                True,
                "Task started successfully",
                serializer.data
            )
            
        except Task.DoesNotExist:
            return self._format_response(
                False,
                "Task not found",
                None,
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self._format_response(
                False,
                str(e),
                None,
                status.HTTP_400_BAD_REQUEST
            )
