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
        if instance:
            # Validate status transitions
            current_status = instance.status
            new_status = data.get('status', current_status)
            
            if current_status == 'completed' and new_status != 'completed':
                raise serializers.ValidationError(
                    "Cannot change status from completed to other statuses"
                )
        
        # Validate worked hours is positive
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