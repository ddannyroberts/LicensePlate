from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import json

from .models import AuthorizedVehicle, AccessLog, VehicleDetection, GateControlLog

@staff_member_required
def authorized_vehicles(request):
    """Manage authorized vehicles"""
    return render(request, 'vehicle_control/authorized_vehicles.html')

@staff_member_required
def add_vehicle(request):
    """Add new authorized vehicle"""
    return render(request, 'vehicle_control/add_vehicle.html')

@staff_member_required
def remove_vehicle(request, vehicle_id):
    """Remove authorized vehicle"""
    return redirect('vehicle_control:authorized_vehicles')

@staff_member_required
def access_logs(request):
    """View access logs"""
    return render(request, 'vehicle_control/access_logs.html')

@login_required
def upload_video(request):
    """Upload video for processing"""
    return render(request, 'vehicle_control/upload_video.html')

@login_required
def process_video(request, detection_id):
    """Process uploaded video"""
    return render(request, 'vehicle_control/process_video.html')

@staff_member_required
def test_gate_control(request):
    """Test gate control functionality"""
    return redirect('/dashboard/admin/')

@csrf_exempt
def video_progress_api(request, detection_id):
    """API endpoint for video processing progress"""
    return JsonResponse({'progress': 0})

@csrf_exempt
def gate_status_api(request):
    """API endpoint for gate status"""
    return JsonResponse({'status': 'CLOSED'})
