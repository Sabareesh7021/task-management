from rest_framework import serializers
from .models import Task
from users.models import User
from users.serializer import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assigned_to',
            'assigned_to_id',
            'assigned_by',
            'due_date',
            'status',
            'completion_report',
            'worked_hours',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'assigned_by',
            'created_at',
            'updated_at'
        ]
    
    
    def validate(self, data):
        """
        Add custom validation for status transitions and worked hours
        """
        instance = self.instance
        request = self.context.get('request')
        
        # For partial updates (PATCH), get existing values from instance
        current_status = instance.status if instance else None
        new_status = data.get('status', current_status)
        
        # Only validate user task limit if this is a status change to in_progress
        if instance and request and new_status == 'in_progress':
            self._validate_user_task_limit(request.user, data)
        
        # Validate status transitions
        if instance and current_status == 'completed' and new_status != 'completed':
            raise serializers.ValidationError(
                "Cannot change status from completed to other statuses"
            )
        
        # Only require completion report and worked hours if status is being set to completed
        if new_status == 'completed':
            if not data.get('completion_report', getattr(instance, 'completion_report', None)):
                raise serializers.ValidationError(
                    "Completion report is required to mark task as complete"
                )
            if data.get('worked_hours') is None and getattr(instance, 'worked_hours', None) is None:
                raise serializers.ValidationError(
                    "Worked hours are required to mark task as complete"
                )
        
        # Validate worked hours is positive if provided
        worked_hours = data.get('worked_hours')
        if worked_hours is not None and worked_hours < 0:
            raise serializers.ValidationError(
                "Worked hours cannot be negative"
            )
        
        return data
    
    def create(self, validated_data):
        """
        Automatically set the assigned_by user from the request context
        """
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)