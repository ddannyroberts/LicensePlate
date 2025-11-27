from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import cv2
import numpy as np
from datetime import datetime, timedelta

from .models import (
    RegisteredLicensePlate, VideoDetection, 
    KnownLicensePlate, UnknownLicensePlate
)
from .detection import AdvancedLicensePlateDetector as LicensePlateDetector

# ==================== USER VIEWS ====================

@login_required
def register_plate(request):
    """User can register license plate with image"""
    if request.method == 'POST':
        plate_number = request.POST.get('plate_number', '').strip().upper()
        plate_image = request.FILES.get('plate_image')
        owner_name = request.POST.get('owner_name', '')
        vehicle_type = request.POST.get('vehicle_type', 'car')
        vehicle_brand = request.POST.get('vehicle_brand', '')
        vehicle_model = request.POST.get('vehicle_model', '')
        vehicle_color = request.POST.get('vehicle_color', '')
        owner_contact = request.POST.get('owner_contact', '')
        notes = request.POST.get('notes', '')
        
        # Validation
        if not plate_number:
            messages.error(request, 'Please enter license plate number')
            return render(request, 'vehicle_control/register_plate.html')
        
        if not plate_image:
            messages.error(request, 'Please upload license plate image')
            return render(request, 'vehicle_control/register_plate.html')
        
        if not owner_name:
            messages.error(request, 'Please enter owner name')
            return render(request, 'vehicle_control/register_plate.html')
        
        # Check if plate already registered by this user
        existing = RegisteredLicensePlate.objects.filter(
            user=request.user,
            plate_number=plate_number
        ).first()
        
        if existing:
            messages.warning(request, f'License plate {plate_number} is already registered by you')
            return render(request, 'vehicle_control/register_plate.html')
        
        # Create registered plate
        try:
            registered_plate = RegisteredLicensePlate.objects.create(
                user=request.user,
                plate_number=plate_number,
                plate_image=plate_image,
                owner_name=owner_name,
                vehicle_type=vehicle_type,
                vehicle_brand=vehicle_brand,
                vehicle_model=vehicle_model,
                vehicle_color=vehicle_color,
                owner_contact=owner_contact,
                notes=notes
            )
            
            messages.success(request, f'License plate {plate_number} registered successfully!')
            return redirect('vehicle_control:my_plates')
            
        except Exception as e:
            messages.error(request, f'Error registering plate: {str(e)}')
    
    return render(request, 'vehicle_control/register_plate.html')

@login_required
def my_plates(request):
    """User can view their registered plates"""
    plates = RegisteredLicensePlate.objects.filter(
        user=request.user
    ).order_by('-registered_date')
    
    return render(request, 'vehicle_control/my_plates.html', {
        'plates': plates
    })

@login_required
def delete_plate(request, plate_id):
    """User can delete their registered plate"""
    plate = get_object_or_404(RegisteredLicensePlate, id=plate_id, user=request.user)
    
    if request.method == 'POST':
        plate_number = plate.plate_number
        plate.delete()
        messages.success(request, f'License plate {plate_number} deleted successfully')
        return redirect('vehicle_control:my_plates')
    
    return render(request, 'vehicle_control/delete_plate.html', {'plate': plate})

# ==================== ADMIN VIEWS ====================

@staff_member_required
def admin_upload_video(request):
    """Admin can upload video for license plate detection"""
    if request.method == 'POST' and 'video' in request.FILES:
        video_file = request.FILES['video']
        
        # Create video detection record
        video_detection = VideoDetection.objects.create(
            uploaded_by=request.user,
            video_file=video_file,
            status='processing'
        )
        
        # Process video in background
        try:
            video_path = video_detection.video_file.path
            process_video_detection(video_detection, video_path)
            
            messages.success(request, f'Video uploaded and processing started! Detection ID: {video_detection.id}')
        except Exception as e:
            video_detection.status = 'error'
            video_detection.processing_notes = str(e)
            video_detection.save()
            messages.error(request, f'Error processing video: {str(e)}')
        
        return redirect('vehicle_control:admin_video_list')
    
    recent_videos = VideoDetection.objects.all().order_by('-upload_timestamp')[:10]
    return render(request, 'vehicle_control/admin_upload_video.html', {
        'recent_videos': recent_videos
    })

def process_video_detection(video_detection, video_path):
    """Process video and detect license plates"""
    from .models import RegisteredLicensePlate, KnownLicensePlate, UnknownLicensePlate
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    detector = AdvancedLicensePlateDetector()
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    frame_skip = 30  # Process every 30th frame
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_skip == 0:
            # Detect license plate
            plate_text, confidence, region = detector.detect_license_plate(frame)
            
            if plate_text and confidence > 0.6:
                # Normalize plate number for comparison
                normalized_plate = plate_text.replace(' ', '').upper()
                
                # Check if plate exists in registered database
                registered_plate = RegisteredLicensePlate.objects.filter(
                    plate_number=normalized_plate
                ).first()
                
                # Save detection image
                detection_image = None
                if region:
                    x, y, w, h = region
                    padding = 10
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(frame.shape[1] - x, w + 2 * padding)
                    h = min(frame.shape[0] - y, h + 2 * padding)
                    crop = frame[y:y+h, x:x+w]
                    
                    # Save image
                    filename = f"detection_{video_detection.id}_{frame_count}_{int(confidence*100)}.jpg"
                    success, buffer = cv2.imencode('.jpg', crop)
                    if success:
                        image_bytes = buffer.tobytes()
                        image_file = ContentFile(image_bytes, name=filename)
                        
                        if registered_plate:
                            detection_image = default_storage.save(f'detections/known/{filename}', image_file)
                        else:
                            detection_image = default_storage.save(f'detections/unknown/{filename}', image_file)
                
                timestamp_seconds = frame_count / fps if fps > 0 else 0
                
                if registered_plate:
                    # Known plate - exists in database
                    KnownLicensePlate.objects.create(
                        video_detection=video_detection,
                        registered_plate=registered_plate,
                        detected_plate_number=plate_text,
                        detection_image=detection_image,
                        confidence_score=confidence,
                        frame_number=frame_count,
                        timestamp_seconds=timestamp_seconds
                    )
                else:
                    # Unknown plate - doesn't exist in database
                    vehicle_type = detector.predict_vehicle_type(frame)
                    UnknownLicensePlate.objects.create(
                        video_detection=video_detection,
                        detected_plate_number=plate_text,
                        detection_image=detection_image,
                        confidence_score=confidence,
                        vehicle_type=vehicle_type,
                        frame_number=frame_count,
                        timestamp_seconds=timestamp_seconds
                    )
        
        frame_count += 1
    
    cap.release()
    
    # Update video detection status
    video_detection.status = 'completed'
    video_detection.processed_at = timezone.now()
    video_detection.save()

@staff_member_required
def admin_video_list(request):
    """Admin can view list of uploaded videos"""
    videos = VideoDetection.objects.all().order_by('-upload_timestamp')
    
    # Statistics
    stats = {
        'total_videos': videos.count(),
        'processing': videos.filter(status='processing').count(),
        'completed': videos.filter(status='completed').count(),
        'error': videos.filter(status='error').count(),
    }
    
    paginator = Paginator(videos, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    return render(request, 'vehicle_control/admin_video_list.html', {
        'videos': page_obj,
        'stats': stats
    })

@staff_member_required
def admin_video_detail(request, video_id):
    """Admin can view details of a video detection"""
    video = get_object_or_404(VideoDetection, id=video_id)
    
    known_plates = KnownLicensePlate.objects.filter(video_detection=video).order_by('-detected_at')
    unknown_plates = UnknownLicensePlate.objects.filter(video_detection=video).order_by('-detected_at')
    
    return render(request, 'vehicle_control/admin_video_detail.html', {
        'video': video,
        'known_plates': known_plates,
        'unknown_plates': unknown_plates
    })

@staff_member_required
def admin_plate_history(request):
    """Admin can view history of all license plates"""
    # Get all registered plates
    registered_plates = RegisteredLicensePlate.objects.all().order_by('-registered_date')
    
    # Get all known detections
    known_detections = KnownLicensePlate.objects.select_related(
        'registered_plate', 'video_detection'
    ).order_by('-detected_at')
    
    # Get all unknown detections
    unknown_detections = UnknownLicensePlate.objects.select_related(
        'video_detection'
    ).order_by('-detected_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        registered_plates = registered_plates.filter(
            Q(plate_number__icontains=search) |
            Q(owner_name__icontains=search)
        )
        known_detections = known_detections.filter(
            Q(detected_plate_number__icontains=search) |
            Q(registered_plate__plate_number__icontains=search)
        )
        unknown_detections = unknown_detections.filter(
            detected_plate_number__icontains=search
        )
    
    # Filter by type
    plate_type = request.GET.get('type', 'all')
    if plate_type == 'registered':
        unknown_detections = unknown_detections.none()
        known_detections = known_detections.none()
    elif plate_type == 'known':
        registered_plates = registered_plates.none()
        unknown_detections = unknown_detections.none()
    elif plate_type == 'unknown':
        registered_plates = registered_plates.none()
        known_detections = known_detections.none()
    
    # Pagination for registered plates
    registered_paginator = Paginator(registered_plates, 20)
    registered_page = request.GET.get('registered_page', 1)
    registered_page_obj = registered_paginator.get_page(registered_page)
    
    # Pagination for known detections
    known_paginator = Paginator(known_detections, 20)
    known_page = request.GET.get('known_page', 1)
    known_page_obj = known_paginator.get_page(known_page)
    
    # Pagination for unknown detections
    unknown_paginator = Paginator(unknown_detections, 20)
    unknown_page = request.GET.get('unknown_page', 1)
    unknown_page_obj = unknown_paginator.get_page(unknown_page)
    
    # Combined timeline - all detections sorted by time
    # Get all detections (before filtering) for timeline
    all_known = KnownLicensePlate.objects.select_related(
        'registered_plate', 'video_detection'
    ).order_by('-detected_at')
    
    all_unknown = UnknownLicensePlate.objects.select_related(
        'video_detection'
    ).order_by('-detected_at')
    
    # Apply search to timeline if provided
    if search:
        all_known = all_known.filter(
            Q(detected_plate_number__icontains=search) |
            Q(registered_plate__plate_number__icontains=search)
        )
        all_unknown = all_unknown.filter(
            detected_plate_number__icontains=search
        )
    
    # Combine known and unknown detections with type indicator
    timeline_items = []
    for known in all_known:
        timeline_items.append({
            'type': 'known',
            'object': known,
            'timestamp': known.detected_at,
            'plate_number': known.detected_plate_number,
            'image': known.detection_image,
            'owner': known.registered_plate.owner_name if known.registered_plate else 'Unknown',
            'confidence': known.confidence_score,
            'video': known.video_detection,
        })
    
    for unknown in all_unknown:
        timeline_items.append({
            'type': 'unknown',
            'object': unknown,
            'timestamp': unknown.detected_at,
            'plate_number': unknown.detected_plate_number,
            'image': unknown.detection_image,
            'owner': None,
            'confidence': unknown.confidence_score,
            'video': unknown.video_detection,
        })
    
    # Sort by timestamp (newest first)
    timeline_items.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Pagination for timeline
    timeline_paginator = Paginator(timeline_items, 50)
    timeline_page = request.GET.get('timeline_page', 1)
    timeline_page_obj = timeline_paginator.get_page(timeline_page)
    
    return render(request, 'vehicle_control/admin_plate_history.html', {
        'registered_plates': registered_page_obj,
        'known_detections': known_page_obj,
        'unknown_detections': unknown_page_obj,
        'timeline_items': timeline_page_obj,
        'search': search,
        'plate_type': plate_type
    })

@staff_member_required
def download_plate_image(request, image_type, image_id):
    """Admin can download license plate images"""
    if image_type == 'registered':
        plate = get_object_or_404(RegisteredLicensePlate, id=image_id)
        if plate.plate_image:
            return FileResponse(plate.plate_image.open(), as_attachment=True, filename=f"plate_{plate.plate_number}.jpg")
    
    elif image_type == 'known':
        detection = get_object_or_404(KnownLicensePlate, id=image_id)
        if detection.detection_image:
            return FileResponse(detection.detection_image.open(), as_attachment=True, filename=f"known_{detection.detected_plate_number}.jpg")
    
    elif image_type == 'unknown':
        detection = get_object_or_404(UnknownLicensePlate, id=image_id)
        if detection.detection_image:
            return FileResponse(detection.detection_image.open(), as_attachment=True, filename=f"unknown_{detection.detected_plate_number}.jpg")
    
    messages.error(request, 'Image not found')
    return redirect('vehicle_control:admin_plate_history')

@staff_member_required
def view_plate_image(request, image_type, image_id):
    """Admin can view license plate images"""
    if image_type == 'registered':
        plate = get_object_or_404(RegisteredLicensePlate, id=image_id)
        if plate.plate_image:
            return FileResponse(plate.plate_image.open(), content_type='image/jpeg')
    
    elif image_type == 'known':
        detection = get_object_or_404(KnownLicensePlate, id=image_id)
        if detection.detection_image:
            return FileResponse(detection.detection_image.open(), content_type='image/jpeg')
    
    elif image_type == 'unknown':
        detection = get_object_or_404(UnknownLicensePlate, id=image_id)
        if detection.detection_image:
            return FileResponse(detection.detection_image.open(), content_type='image/jpeg')
    
    return HttpResponse('Image not found', status=404)
