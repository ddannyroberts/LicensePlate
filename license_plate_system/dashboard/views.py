from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from vehicle_control.models import (
    RegisteredLicensePlate, VideoDetection,
    KnownLicensePlate, UnknownLicensePlate
)

@login_required
def home_dashboard(request):
    """Main user dashboard"""
    user = request.user
    
    # Get user's registered plates
    recent_plates = RegisteredLicensePlate.objects.filter(
        user=user
    ).order_by('-registered_date')[:10]
    
    # Statistics
    stats = {
        'total_plates': RegisteredLicensePlate.objects.filter(user=user).count(),
        'recent_plates': recent_plates.count(),
    }
    
    if user.is_staff:
        stats.update({
            'total_registered_plates': RegisteredLicensePlate.objects.count(),
            'total_videos': VideoDetection.objects.count(),
            'total_known_detections': KnownLicensePlate.objects.count(),
            'total_unknown_detections': UnknownLicensePlate.objects.count(),
        })
    
    context = {
        'recent_plates': recent_plates,
        'stats': stats,
        'user': user,
    }
    
    return render(request, 'dashboard/home.html', context)

@staff_member_required
def admin_dashboard(request):
    """Admin-only dashboard with comprehensive statistics"""
    
    # Time ranges for statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic statistics
    stats = {
        'total_registered_plates': RegisteredLicensePlate.objects.count(),
        'total_videos': VideoDetection.objects.count(),
        'total_known_detections': KnownLicensePlate.objects.count(),
        'total_unknown_detections': UnknownLicensePlate.objects.count(),
        'today_videos': VideoDetection.objects.filter(upload_timestamp__date=today).count(),
        'week_videos': VideoDetection.objects.filter(upload_timestamp__date__gte=week_ago).count(),
        'month_videos': VideoDetection.objects.filter(upload_timestamp__date__gte=month_ago).count(),
    }
    
    # Recent activity
    recent_videos = VideoDetection.objects.select_related('uploaded_by').order_by('-upload_timestamp')[:15]
    recent_known = KnownLicensePlate.objects.select_related('registered_plate', 'video_detection').order_by('-detected_at')[:20]
    recent_unknown = UnknownLicensePlate.objects.select_related('video_detection').order_by('-detected_at')[:20]
    
    # Top registered plates
    top_plates = RegisteredLicensePlate.objects.annotate(
        detection_count=Count('video_detections')
    ).order_by('-detection_count')[:10]
    
    context = {
        'stats': stats,
        'recent_videos': recent_videos,
        'recent_known': recent_known,
        'recent_unknown': recent_unknown,
        'top_plates': top_plates,
        'today': today,
    }
    
    return render(request, 'dashboard/admin.html', context)

