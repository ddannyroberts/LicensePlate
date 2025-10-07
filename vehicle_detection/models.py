"""
Vehicle Detection models - Migrated from Flask models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import os

User = get_user_model()


class VehicleLog(models.Model):
    """
    Vehicle detection log - Migrated from Flask VehicleLog model

    Original Flask model:
    class VehicleLog(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        plate_text = db.Column(db.String(100))
        vendor = db.Column(db.String(100))
        model = db.Column(db.String(100))
        color = db.Column(db.String(100))
        province = db.Column(db.String(100))
        category = db.Column(db.String(100))
        image_filename = db.Column(db.String(100))
        video_filename = db.Column(db.String(100))
        status = db.Column(db.String(50))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    """

    STATUS_CHOICES = [
        ('entry', 'Manual Entry'),
        ('known', 'Known Vehicle'),
        ('unknown', 'Unknown Vehicle'),
        ('authorized', 'Authorized'),
        ('unauthorized', 'Unauthorized'),
        ('detected_live', 'Live Detection'),
    ]

    CATEGORY_CHOICES = [
        ('Car', 'Car'),
        ('Truck', 'Truck'),
        ('SUV', 'SUV'),
        ('Motorcycle', 'Motorcycle'),
        ('Van', 'Van'),
        ('Bus', 'Bus'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicle_logs'
    )
    plate_text = models.CharField(max_length=100, blank=True, null=True)
    vendor = models.CharField('Brand', max_length=100, blank=True, null=True)
    model = models.CharField('Car Model', max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )
    image_filename = models.CharField(max_length=100, blank=True, null=True)
    video_filename = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='unknown'
    )
    confidence = models.FloatField(default=0.0, help_text='Detection confidence score')
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'vehiclelog'
        ordering = ['-timestamp']
        verbose_name = 'Vehicle Log'
        verbose_name_plural = 'Vehicle Logs'

    def __str__(self):
        return f"{self.plate_text or 'Unknown'} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def image_url(self):
        """Get full URL for image file"""
        if self.image_filename:
            return f"/media/uploads/{self.image_filename}"
        return None

    @property
    def video_url(self):
        """Get full URL for video file"""
        if self.video_filename:
            return f"/media/videos/{self.video_filename}"
        return None


class AuthorizedVehicle(models.Model):
    """
    Authorized vehicles database - Migrated from Flask AuthorizedVehicle model

    Original Flask model:
    class AuthorizedVehicle(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        plate_number = db.Column(db.String(20), unique=True, nullable=False)
        owner_name = db.Column(db.String(100), nullable=False)
        vehicle_type = db.Column(db.String(50), default="Car")
        access_level = db.Column(db.String(20), default="full")
        registered_date = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)
    """

    ACCESS_LEVEL_CHOICES = [
        ('full', 'Full Access'),
        ('limited', 'Limited Access'),
        ('temporary', 'Temporary Access'),
    ]

    VEHICLE_TYPE_CHOICES = [
        ('Car', 'Car'),
        ('SUV', 'SUV'),
        ('Truck', 'Truck'),
        ('Motorcycle', 'Motorcycle'),
        ('Van', 'Van'),
        ('Bus', 'Bus'),
        ('Other', 'Other'),
    ]

    plate_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='License plate number (normalized)'
    )
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    vehicle_type = models.CharField(
        max_length=50,
        choices=VEHICLE_TYPE_CHOICES,
        default='Car'
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='full'
    )
    registered_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'authorizedvehicle'
        ordering = ['-registered_date']
        verbose_name = 'Authorized Vehicle'
        verbose_name_plural = 'Authorized Vehicles'

    def __str__(self):
        return f"{self.plate_number} - {self.owner_name}"

    def save(self, *args, **kwargs):
        # Normalize plate number
        if self.plate_number:
            self.plate_number = self.plate_number.upper().replace(' ', '')
        super().save(*args, **kwargs)


class AccessLog(models.Model):
    """
    Access attempt logging - Migrated from Flask AccessLog model

    Original Flask model:
    class AccessLog(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        plate_number = db.Column(db.String(20), nullable=False)
        authorized = db.Column(db.Boolean, nullable=False)
        confidence = db.Column(db.Float, nullable=False)
        gate_action = db.Column(db.String(20), nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        owner_info = db.Column(db.Text)  # JSON string
        entry_type = db.Column(db.String(10), default="ENTRY")  # ENTRY or EXIT
    """

    ENTRY_TYPE_CHOICES = [
        ('ENTRY', 'Entry'),
        ('EXIT', 'Exit'),
    ]

    GATE_ACTION_CHOICES = [
        ('OPENED', 'Gate Opened'),
        ('DENIED', 'Access Denied'),
        ('MANUAL', 'Manual Override'),
    ]

    plate_number = models.CharField(max_length=20)
    authorized = models.BooleanField()
    confidence = models.FloatField(help_text='Detection confidence score')
    gate_action = models.CharField(
        max_length=20,
        choices=GATE_ACTION_CHOICES
    )
    timestamp = models.DateTimeField(default=timezone.now)
    owner_info = models.JSONField(blank=True, null=True)  # Store as JSON
    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES,
        default='ENTRY'
    )

    # Additional fields for better tracking
    authorized_vehicle = models.ForeignKey(
        AuthorizedVehicle,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='access_logs'
    )
    detection_source = models.CharField(
        max_length=50,
        default='video_upload',
        help_text='Source of detection (video_upload, live_camera, manual, etc.)'
    )

    class Meta:
        db_table = 'accesslog'
        ordering = ['-timestamp']
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'

    def __str__(self):
        status = '✅ Authorized' if self.authorized else '❌ Denied'
        return f"{self.plate_number} - {status} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class VehicleStatus(models.Model):
    """
    Current vehicle status (inside/outside premises) - Migrated from Flask VehicleStatus model

    Original Flask model:
    class VehicleStatus(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        plate_number = db.Column(db.String(20), nullable=False, unique=True)
        status = db.Column(db.String(10), nullable=False)  # INSIDE, OUTSIDE
        entry_time = db.Column(db.DateTime)
        exit_time = db.Column(db.DateTime)
        duration = db.Column(db.Integer)  # Duration in minutes
        last_updated = db.Column(db.DateTime, default=datetime.utcnow)
        owner_info = db.Column(db.Text)
    """

    STATUS_CHOICES = [
        ('INSIDE', 'Inside Premises'),
        ('OUTSIDE', 'Outside Premises'),
    ]

    plate_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )
    entry_time = models.DateTimeField(blank=True, null=True)
    exit_time = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(
        blank=True,
        null=True,
        help_text='Duration in minutes'
    )
    last_updated = models.DateTimeField(default=timezone.now)
    owner_info = models.JSONField(blank=True, null=True)

    # Link to authorized vehicle
    authorized_vehicle = models.OneToOneField(
        AuthorizedVehicle,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='current_status'
    )

    class Meta:
        db_table = 'vehiclestatus'
        ordering = ['-last_updated']
        verbose_name = 'Vehicle Status'
        verbose_name_plural = 'Vehicle Statuses'

    def __str__(self):
        return f"{self.plate_number} - {self.status}"

    def save(self, *args, **kwargs):
        # Calculate duration when status changes to OUTSIDE
        if self.status == 'OUTSIDE' and self.entry_time and self.exit_time:
            duration_seconds = (self.exit_time - self.entry_time).total_seconds()
            self.duration = int(duration_seconds / 60)  # Convert to minutes

        super().save(*args, **kwargs)


class SystemStats(models.Model):
    """
    Daily system statistics - Migrated from Flask SystemStats model

    Original Flask model:
    class SystemStats(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        date = db.Column(db.Date, default=datetime.utcnow)
        total_entries = db.Column(db.Integer, default=0)
        total_exits = db.Column(db.Integer, default=0)
        authorized_entries = db.Column(db.Integer, default=0)
        unauthorized_attempts = db.Column(db.Integer, default=0)
        vehicles_inside = db.Column(db.Integer, default=0)
        peak_occupancy = db.Column(db.Integer, default=0)
        last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    """

    date = models.DateField(unique=True, default=timezone.now)
    total_entries = models.IntegerField(default=0)
    total_exits = models.IntegerField(default=0)
    authorized_entries = models.IntegerField(default=0)
    unauthorized_attempts = models.IntegerField(default=0)
    vehicles_inside = models.IntegerField(default=0)
    peak_occupancy = models.IntegerField(default=0)
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'systemstats'
        ordering = ['-date']
        verbose_name = 'System Statistics'
        verbose_name_plural = 'System Statistics'

    def __str__(self):
        return f"Stats for {self.date.strftime('%Y-%m-%d')}"