from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from vehicle_control.models import (
    RegisteredLicensePlate, VideoDetection,
    KnownLicensePlate, UnknownLicensePlate
)

# Customize admin site
admin.site.site_header = "License Plate Detection System"
admin.site.site_title = "LPR Admin"
admin.site.index_title = "Welcome to License Plate Detection System Administration"

# Override admin index view to add statistics
original_index = admin.site.index

def custom_index(request, extra_context=None):
    """Custom admin index with statistics"""
    extra_context = extra_context or {}
    
    # Get statistics
    stats = {
        'total_registered_plates': RegisteredLicensePlate.objects.count(),
        'total_videos': VideoDetection.objects.count(),
        'total_known_detections': KnownLicensePlate.objects.count(),
        'total_unknown_detections': UnknownLicensePlate.objects.count(),
    }
    
    extra_context['stats'] = stats
    return original_index(request, extra_context)

# Replace the index view
admin.site.index = custom_index
