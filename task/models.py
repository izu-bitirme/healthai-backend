from django.db import models
from django.contrib.auth.models import User
from user_profile.models import Patient


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]


    STATUE_COLOR_MAPPING = {
        'pending': 'badge-light-warning',
        'in_progress': 'badge-light-primary',
        'completed': 'badge-light-success',
        'overdue': 'badge-light-danger',
    }
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.patient.profile.user.username}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and not self.is_completed

    def get_status_color(self):
        return self.STATUE_COLOR_MAPPING.get(self.status, 'pending')