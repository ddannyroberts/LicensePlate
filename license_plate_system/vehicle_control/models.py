from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class AuthorizedVehicle(models.Model):
    """Authorized vehicles for access control"""
    ACCESS_LEVELS = [
        ('full', 'Full Access'),
        ('limited', 'Limited Access'), 
        ('visitor', 'Visitor Access'),
        ('emergency', 'Emergency Access'),
    ]
    
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('van', 'Van'),
        ('bus', 'Bus'),
        ('other', 'Other'),
    ]
    
    plate_number = models.CharField(max_length=20, unique=True)
    owner_name = models.CharField(max_length=100)
    owner_contact = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='car')
    vehicle_brand = models.CharField(max_length=50, blank=True)
    vehicle_model = models.CharField(max_length=50, blank=True)
    vehicle_color = models.CharField(max_length=30, blank=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='full')
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    registered_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-registered_date']
    
    def __str__(self):
        return f"{self.plate_number} - {self.owner_name}"
    
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False

class AccessLog(models.Model):
    """Log of all access attempts"""
    GATE_ACTIONS = [
        ('opened', 'Gate Opened'),
        ('denied', 'Access Denied'),
        ('manual_open', 'Manual Override'),
        ('error', 'System Error'),
    ]
    
    plate_number = models.CharField(max_length=20)
    authorized = models.BooleanField()
    confidence = models.FloatField()
    gate_action = models.CharField(max_length=20, choices=GATE_ACTIONS)
    vehicle = models.ForeignKey(AuthorizedVehicle, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    owner_info = models.JSONField(default=dict, blank=True)
    detection_image = models.ImageField(upload_to='detections/', null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        status = "✅" if self.authorized else "❌"
        return f"{status} {self.plate_number} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class VehicleDetection(models.Model):
    """Vehicle detection results from video processing"""
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('authorized', 'Authorized'),
        ('unauthorized', 'Unauthorized'),
    ]
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='videos/')
    plate_text = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=50, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    detection_image = models.ImageField(upload_to='detections/', null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)
    processing_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-upload_timestamp']
    
    def __str__(self):
        return f"Detection {self.id} - {self.plate_text or 'Processing...'}"

class SystemSettings(models.Model):
    """System configuration settings"""
    setting_name = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    description = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.setting_name
    
    @classmethod
    def get_setting(cls, name, default=None):
        try:
            setting = cls.objects.get(setting_name=name)
            return setting.setting_value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, name, value, user=None, description=""):
        setting, created = cls.objects.get_or_create(
            setting_name=name,
            defaults={
                'setting_value': value,
                'description': description,
                'modified_by': user
            }
        )
        if not created:
            setting.setting_value = value
            setting.modified_by = user
            setting.save()
        return setting

class GateControlLog(models.Model):
    """Physical gate control operations log"""
    OPERATIONS = [
        ('open', 'Gate Opened'),
        ('close', 'Gate Closed'),
        ('auto_close', 'Auto Close'),
        ('manual_override', 'Manual Override'),
        ('emergency_open', 'Emergency Open'),
        ('maintenance', 'Maintenance Mode'),
    ]
    
    operation = models.CharField(max_length=20, choices=OPERATIONS)
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    related_access_log = models.ForeignKey(AccessLog, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    duration_seconds = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_operation_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
