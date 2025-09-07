from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class VehicleLog(models.Model):
    STATUS_CHOICES = [
        ('entry', 'Entry'),
        ('known', 'Known'),
        ('unknown', 'Unknown'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plate_text = models.CharField(max_length=100, blank=True, null=True)
    vendor = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    image_filename = models.CharField(max_length=100, blank=True, null=True)
    video_filename = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unknown')
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'vehicle_log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.plate_text} - {self.status}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {'Admin' if self.is_admin else 'User'}"
