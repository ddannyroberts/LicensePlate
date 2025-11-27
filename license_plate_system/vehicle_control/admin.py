from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    UserProfile, RegisteredLicensePlate, 
    VideoDetection, KnownLicensePlate, UnknownLicensePlate
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'address']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['user__is_staff', 'user__is_active']

@admin.register(RegisteredLicensePlate)
class RegisteredLicensePlateAdmin(admin.ModelAdmin):
    list_display = ['plate_image_preview', 'plate_number', 'owner_name', 'vehicle_type', 'user', 'registered_date']
    search_fields = ['plate_number', 'owner_name', 'owner_contact', 'user__username']
    list_filter = ['vehicle_type', 'registered_date']
    readonly_fields = ['registered_date', 'plate_image_preview']
    fieldsets = (
        ('License Plate Information', {
            'fields': ('plate_number', 'plate_image', 'plate_image_preview', 'user')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'owner_contact')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_brand', 'vehicle_model', 'vehicle_color')
        }),
        ('Additional Information', {
            'fields': ('notes', 'registered_date')
        }),
    )
    
    def plate_image_preview(self, obj):
        if obj.plate_image:
            return format_html(
                '<img src="{}" width="100" height="auto" style="border-radius: 8px;" />',
                obj.plate_image.url
            )
        return "No image"
    plate_image_preview.short_description = 'Image Preview'

@admin.register(VideoDetection)
class VideoDetectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'uploaded_by', 'status', 'upload_timestamp', 'processed_at']
    search_fields = ['uploaded_by__username']
    list_filter = ['status', 'upload_timestamp']
    readonly_fields = ['upload_timestamp', 'processed_at']
    date_hierarchy = 'upload_timestamp'

@admin.register(KnownLicensePlate)
class KnownLicensePlateAdmin(admin.ModelAdmin):
    list_display = ['detection_image_preview', 'detected_plate_number', 'registered_plate', 'confidence_score', 'video_detection', 'detected_at']
    search_fields = ['detected_plate_number', 'registered_plate__plate_number', 'registered_plate__owner_name']
    list_filter = ['detected_at', 'confidence_score']
    readonly_fields = ['detected_at', 'detection_image_preview']
    date_hierarchy = 'detected_at'
    
    def detection_image_preview(self, obj):
        if obj.detection_image:
            return format_html(
                '<img src="{}" width="100" height="auto" style="border-radius: 8px;" />',
                obj.detection_image.url
            )
        return "No image"
    detection_image_preview.short_description = 'Detection Image'

@admin.register(UnknownLicensePlate)
class UnknownLicensePlateAdmin(admin.ModelAdmin):
    list_display = ['detection_image_preview', 'detected_plate_number', 'vehicle_type', 'confidence_score', 'video_detection', 'detected_at']
    search_fields = ['detected_plate_number', 'vehicle_type']
    list_filter = ['detected_at', 'confidence_score', 'vehicle_type']
    readonly_fields = ['detected_at', 'detection_image_preview']
    date_hierarchy = 'detected_at'
    
    def detection_image_preview(self, obj):
        if obj.detection_image:
            return format_html(
                '<img src="{}" width="100" height="auto" style="border-radius: 8px;" />',
                obj.detection_image.url
            )
        return "No image"
    detection_image_preview.short_description = 'Detection Image'
