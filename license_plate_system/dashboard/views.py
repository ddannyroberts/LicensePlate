from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from vehicle_control.models import (
    AuthorizedVehicle, AccessLog, VehicleDetection, 
    GateControlLog, SystemSettings
)

@login_required
def home_dashboard(request):
    """Main user dashboard"""
    user = request.user
    
    # Get user's recent detections
    recent_detections = VehicleDetection.objects.filter(
        uploaded_by=user
    ).order_by('-upload_timestamp')[:10]
    
    # Get user's recent access logs if admin
    recent_access = []
    if user.is_staff:
        recent_access = AccessLog.objects.all().order_by('-timestamp')[:20]
    
    # Statistics
    stats = {
        'total_detections': VehicleDetection.objects.filter(uploaded_by=user).count(),
        'successful_detections': VehicleDetection.objects.filter(
            uploaded_by=user, status__in=['completed', 'authorized', 'unauthorized']
        ).count(),
    }
    
    if user.is_staff:
        stats.update({
            'total_authorized_vehicles': AuthorizedVehicle.objects.filter(is_active=True).count(),
            'today_access_attempts': AccessLog.objects.filter(
                timestamp__date=timezone.now().date()
            ).count(),
            'authorized_today': AccessLog.objects.filter(
                timestamp__date=timezone.now().date(),
                authorized=True
            ).count(),
        })
    
    context = {
        'recent_detections': recent_detections,
        'recent_access': recent_access,
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
        'total_vehicles': AuthorizedVehicle.objects.filter(is_active=True).count(),
        'total_users': VehicleDetection.objects.values('uploaded_by').distinct().count(),
        'today_access': AccessLog.objects.filter(timestamp__date=today).count(),
        'today_authorized': AccessLog.objects.filter(
            timestamp__date=today, authorized=True
        ).count(),
        'week_access': AccessLog.objects.filter(timestamp__date__gte=week_ago).count(),
        'month_detections': VehicleDetection.objects.filter(
            upload_timestamp__date__gte=month_ago
        ).count(),
    }
    
    # Recent activity
    recent_access_logs = AccessLog.objects.select_related('vehicle').order_by('-timestamp')[:20]
    recent_detections = VehicleDetection.objects.select_related('uploaded_by').order_by('-upload_timestamp')[:15]
    recent_gate_logs = GateControlLog.objects.select_related('triggered_by').order_by('-timestamp')[:10]
    
    # Top authorized vehicles (most accessed)
    top_vehicles = AccessLog.objects.filter(
        authorized=True, 
        timestamp__date__gte=week_ago
    ).values('plate_number').annotate(
        access_count=Count('id')
    ).order_by('-access_count')[:10]
    
    context = {
        'stats': stats,
        'recent_access_logs': recent_access_logs,
        'recent_detections': recent_detections,
        'recent_gate_logs': recent_gate_logs,
        'top_vehicles': top_vehicles,
        'today': today,
    }
    
    return render(request, 'dashboard/admin.html', context)

@staff_member_required
def analytics_view(request):
    """Advanced analytics and reporting"""
    return render(request, 'dashboard/analytics.html')

@staff_member_required
def settings_view(request):
    """System settings management"""
    return render(request, 'dashboard/settings.html')
