from django.db import models
from users.models import User


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_rogress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('overdue', 'Overdue'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_by')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"
    
    class Meta:
        db_table = "tasks"
        ordering = ['-created_at']