"""
Vehicle Detection views - Migrated from Flask routes
"""
import os
import cv2
import json
import numpy as np
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from .models import VehicleLog, AuthorizedVehicle, AccessLog, SystemStats
from .detection_engine import AdvancedLicensePlateDetector
from arduino_integration.services import ArduinoService

# Initialize detection engine
detector = AdvancedLicensePlateDetector()
arduino_service = ArduinoService()


@login_required
def dashboard_view(request):
    """
    Main dashboard - Migrated from Flask dashboard route

    Original Flask route:
    @app.route('/dashboard', methods=['GET', 'POST'])
    """
    if request.method == 'POST':
        # Handle video upload
        if 'video' in request.FILES:
            return handle_video_upload(request)

        # Handle manual form submission
        plate_text = request.POST.get('plate_text', '')
        province = request.POST.get('province', '')
        brand = request.POST.get('brand', '')
        model = request.POST.get('model', '')
        category = request.POST.get('category', '')
        image = request.FILES.get('image')

        if image:
            # Save image
            filename = default_storage.save(f'uploads/{image.name}', ContentFile(image.read()))

            # Create vehicle log entry
            VehicleLog.objects.create(
                user=request.user,
                plate_text=plate_text,
                vendor=brand,
                model=model,
                color='-',
                province=province,
                category=category,
                image_filename=filename,
                status='entry'
            )
            messages.success(request, 'Vehicle submitted successfully!')

    # Get user's vehicle logs
    plates = VehicleLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'vehicle_detection/dashboard.html', {
        'plates': plates,
        'username': request.user.username
    })


def handle_video_upload(request):
    """
    Handle video file upload and processing
    Migrated from Flask handle_video_upload function
    """
    video_file = request.FILES.get('video')
    if not video_file:
        messages.error(request, 'No video file selected')
        return redirect('dashboard')

    # Save video file
    filename = default_storage.save(f'videos/{video_file.name}', ContentFile(video_file.read()))
    video_path = default_storage.path(filename)

    # Process video for license plate detection
    cap = cv2.VideoCapture(video_path)
    results = []
    frame_count = 0
    frame_skip = 30

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            # Detect license plate
            plate_text, confidence, region = detector.detect_license_plate(frame)

            if plate_text and confidence > 0.6:
                # Check authorization
                is_authorized = check_authorization(plate_text)

                # Save the cropped plate image
                crop_filename = None
                if region:
                    x, y, w, h = region
                    padding = 10
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(frame.shape[1] - x, w + 2 * padding)
                    h = min(frame.shape[0] - y, h + 2 * padding)
                    crop = frame[y:y+h, x:x+w]

                    crop_filename = f"plate_{request.user.id}_{frame_count}_{confidence:.2f}.jpg"
                    crop_path = os.path.join(settings.MEDIA_ROOT, 'uploads', crop_filename)
                    cv2.imwrite(crop_path, crop)

                # Save to vehicle log
                vehicle_log = VehicleLog.objects.create(
                    user=request.user,
                    plate_text=plate_text,
                    vendor=detector.predict_vehicle_type(frame),
                    video_filename=filename,
                    image_filename=crop_filename,
                    status='authorized' if is_authorized else 'unauthorized',
                    confidence=confidence
                )

                # Save to access log
                AccessLog.objects.create(
                    plate_number=plate_text,
                    authorized=is_authorized,
                    confidence=confidence,
                    gate_action='OPENED' if is_authorized else 'DENIED',
                    detection_source='video_upload'
                )

                # Send command to Arduino if authorized
                if is_authorized:
                    authorized_vehicle = AuthorizedVehicle.objects.filter(
                        plate_number=plate_text.upper().replace(' ', '')
                    ).first()

                    owner_name = authorized_vehicle.owner_name if authorized_vehicle else 'Unknown'
                    arduino_result = arduino_service.open_gate(plate_text, owner_name, True)

                results.append({
                    'plate_text': plate_text,
                    'confidence': confidence,
                    'authorized': is_authorized
                })

        frame_count += 1

    cap.release()

    messages.success(request, f'Video processed successfully! Found {len(results)} license plates.')
    return redirect('dashboard')


def check_authorization(plate_text):
    """Check if a license plate is authorized"""
    normalized_plate = plate_text.upper().replace(' ', '')
    return AuthorizedVehicle.objects.filter(
        plate_number=normalized_plate,
        is_active=True
    ).exists()


@csrf_exempt
@require_http_methods(["POST"])
def process_video_api(request):
    """
    AJAX endpoint for video processing
    Migrated from Flask @app.route('/process-video', methods=['POST'])
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        video_file = request.FILES.get('video')
        if not video_file:
            return JsonResponse({'error': 'No video file'}, status=400)

        # Process video
        filename = default_storage.save(f'videos/{video_file.name}', ContentFile(video_file.read()))
        video_path = default_storage.path(filename)

        results = detector.process_video_file(video_path)

        processed_results = []
        for i, result in enumerate(results):
            if result['plate_text'] != 'UNKNOWN':
                crop_filename = None
                if result['plate_crop'] is not None:
                    crop_filename = f"plate_{request.user.id}_{i}_{result['timestamp']:.1f}.jpg"
                    crop_path = os.path.join(settings.MEDIA_ROOT, 'uploads', crop_filename)
                    cv2.imwrite(crop_path, result['plate_crop'])

                VehicleLog.objects.create(
                    user=request.user,
                    plate_text=result['plate_text'],
                    vendor=result['vehicle_type'],
                    video_filename=filename,
                    image_filename=crop_filename,
                    status='unknown',
                    confidence=0.9  # Default confidence for processed video
                )

                processed_results.append({
                    'plate_text': result['plate_text'],
                    'vehicle_type': result['vehicle_type'],
                    'timestamp': result['timestamp']
                })

        return JsonResponse({
            'success': True,
            'message': f'Video processed successfully! Found {len(processed_results)} license plates.',
            'results': processed_results
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def detect_frame_api(request):
    """
    API endpoint for real-time frame detection
    Migrated from Flask @app.route('/api/detect_frame', methods=['POST'])
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        frame_file = request.FILES.get('frame')
        if not frame_file:
            return JsonResponse({'error': 'No frame provided'}, status=400)

        # Read image data
        frame_data = frame_file.read()
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return JsonResponse({'error': 'Invalid image data'}, status=400)

        # Detect license plates
        plate_text, confidence, region = detector.detect_license_plate(frame)

        plates = []
        if plate_text and confidence > 0.6:
            plates.append({
                'text': plate_text,
                'confidence': confidence,
                'bbox': region if region else [],
                'cleaned_text': plate_text
            })

        return JsonResponse({
            'success': True,
            'plates': plates,
            'count': len(plates),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Detection failed: {str(e)}',
            'plates': [],
            'count': 0
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_detected_plate_api(request):
    """
    API endpoint to auto-save detected plates from live camera
    Migrated from Flask @app.route('/api/save_detected_plate', methods=['POST'])
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        data = json.loads(request.body)

        plate_text = data.get('plate_text', '').strip().upper()
        confidence = data.get('confidence', 0.0)
        source = data.get('source', 'live_camera')

        if not plate_text:
            return JsonResponse({'error': 'No plate text provided'}, status=400)

        # Check for recent duplicates
        recent_detection = VehicleLog.objects.filter(
            plate_text=plate_text,
            user=request.user,
            timestamp__gte=datetime.now() - timedelta(seconds=30)
        ).first()

        if recent_detection:
            return JsonResponse({
                'message': 'Duplicate detection ignored (too recent)',
                'saved': False
            })

        # Save new detection
        detection = VehicleLog.objects.create(
            user=request.user,
            plate_text=plate_text,
            confidence=confidence,
            status='detected_live',
            category='Unknown',
            province='Auto-detected',
            vendor='Live Camera'
        )

        return JsonResponse({
            'success': True,
            'message': f'Plate {plate_text} saved successfully',
            'saved': True,
            'detection_id': detection.id
        })

    except Exception as e:
        return JsonResponse({'error': f'Save failed: {str(e)}'}, status=500)