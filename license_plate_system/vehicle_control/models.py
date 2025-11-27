from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class RegisteredLicensePlate(models.Model):
    """License plates registered by users"""
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('van', 'Van'),
        ('bus', 'Bus'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_plates')
    plate_number = models.CharField(max_length=20)
    plate_image = models.ImageField(upload_to='registered_plates/')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='car')
    owner_name = models.CharField(max_length=100)
    owner_contact = models.CharField(max_length=50, blank=True)
    vehicle_brand = models.CharField(max_length=50, blank=True)
    vehicle_model = models.CharField(max_length=50, blank=True)
    vehicle_color = models.CharField(max_length=30, blank=True)
    registered_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-registered_date']
        verbose_name = 'Registered License Plate'
        verbose_name_plural = 'Registered License Plates'
    
    def __str__(self):
        return f"{self.plate_number} - {self.owner_name}"

class VideoDetection(models.Model):
    """Video uploaded by admin for license plate detection"""
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='videos/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    upload_timestamp = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-upload_timestamp']
        verbose_name = 'Video Detection'
        verbose_name_plural = 'Video Detections'
    
    def __str__(self):
        return f"Video {self.id} - {self.status}"

class KnownLicensePlate(models.Model):
    """License plates found in video that exist in registered database"""
    video_detection = models.ForeignKey(VideoDetection, on_delete=models.CASCADE, related_name='known_plates')
    registered_plate = models.ForeignKey(RegisteredLicensePlate, on_delete=models.CASCADE, related_name='video_detections')
    detected_plate_number = models.CharField(max_length=20)
    detection_image = models.ImageField(upload_to='detections/known/')
    confidence_score = models.FloatField()
    detected_at = models.DateTimeField(default=timezone.now)
    frame_number = models.IntegerField(null=True, blank=True)
    timestamp_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Known License Plate Detection'
        verbose_name_plural = 'Known License Plate Detections'
    
    def __str__(self):
        return f"{self.detected_plate_number} (Known) - {self.video_detection.id}"

class UnknownLicensePlate(models.Model):
    """License plates found in video that don't exist in registered database"""
    video_detection = models.ForeignKey(VideoDetection, on_delete=models.CASCADE, related_name='unknown_plates')
    detected_plate_number = models.CharField(max_length=20)
    detection_image = models.ImageField(upload_to='detections/unknown/')
    confidence_score = models.FloatField()
    detected_at = models.DateTimeField(default=timezone.now)
    frame_number = models.IntegerField(null=True, blank=True)
    timestamp_seconds = models.FloatField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Unknown License Plate Detection'
        verbose_name_plural = 'Unknown License Plate Detections'
    
    def __str__(self):
        return f"{self.detected_plate_number} (Unknown) - {self.video_detection.id}"
