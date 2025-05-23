from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import Task
from .serializer import TaskSerializer
from utils.pagination import paginate

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class TaskAPIView(APIView):
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

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Task.objects.all()
        elif user.is_staff:
            return Task.objects.filter(
                Q(assigned_to=user) | Q(assigned_by=user)
            )
        return Task.objects.filter(assigned_to=user)

    def get_object(self, pk):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=pk)

    def _format_response(self, status_bool, message=None, data=None, status_code=status.HTTP_200_OK, pagination = None):
        response_data = {
            'status': status_bool,
            'message': message,
            'data': data
        }
        if pagination:
            response_data['total_pages'] = pagination.num_pages
            response_data['total_items'] = pagination.count
            response_data['current_page'] = pagination.number

        return Response(response_data, status=status_code)

    def get(self, request, pk=None):
        try:
            if pk:
                task = self.get_object(pk)
                serializer = TaskSerializer(task)
                return self._format_response(
                    True,
                    'Task retrieved successfully',
                    serializer.data
                )
            
            tasks          = self.get_queryset()
            
            paginated_data = paginate(tasks, request)
            serializer     = TaskSerializer(paginated_data['data'], many=True)

            return self._format_response(
                True,
                'Tasks list retrieved successfully',
                serializer.data,
                status.HTTP_200_OK,
                paginated_data
            )
        except Exception as e:
            return self._format_response(
                False,
                str(e),
                None,
                status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        try:
            serializer = TaskSerializer(
                data=request.data, 
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(assigned_by=request.user)
            return self._format_response(
                True,
                'Task created successfully',
                serializer.data,
                status.HTTP_201_CREATED
            )
        except Exception as e:
            return self._format_response(
                False,
                str(e),
                None,
                status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, pk):
        try:
            task = self.get_object(pk)
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
                'Task updated successfully',
                serializer.data
            )
        except PermissionDenied as e:
            return self._format_response(
                False,
                str(e),
                None,
                status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return self._format_response(
                False,
                str(e),
                None,
                status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        try:
            task = self.get_object(pk)
            task.delete()
            return self._format_response(
                True,
                'Task deleted successfully',
                None,
                status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return self._format_response(
                False,
                str(e),
                None,
                status.HTTP_400_BAD_REQUEST
            )

    def _validate_user_update_permissions(self, user, task, data):
        if user.is_staff or user.is_superuser:
            return
            
        allowed_fields = {'status', 'completion_report', 'worked_hours'}
        if not allowed_fields.issuperset(data.keys()):
            raise PermissionDenied(
                "You can only update status, completion report, and worked hours"
            )
        
        if task.assigned_to != user:
            raise PermissionDenied(
                "You can only update tasks assigned to you"
            )