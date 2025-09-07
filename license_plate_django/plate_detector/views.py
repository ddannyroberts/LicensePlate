from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import VehicleLog, UserProfile
from .utils import LicensePlateDetector
import os
import cv2
import json

detector = LicensePlateDetector()

def home(request):
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user)
        messages.success(request, 'Registration successful!')
        return redirect('login')
    
    return render(request, 'registration/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Check if user is admin
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.is_admin:
                    return redirect('admin_dashboard')
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user)
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Check if user is admin (admin should not access regular dashboard)
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.is_admin:
            return redirect('admin_dashboard')
    except UserProfile.DoesNotExist:
        pass
    
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
        
        log_entry = VehicleLog.objects.create(
            user=request.user,
            plate_text=plate_text,
            vendor=brand,
            model=model,
            province=province,
            category=category,
            status='entry'
        )
        
        messages.success(request, 'Vehicle submitted successfully!')
    
    # Get user's vehicle logs
    plates = VehicleLog.objects.filter(user=request.user).order_by('-timestamp')
    
    return render(request, 'plate_detector/dashboard.html', {
        'plates': plates,
        'username': request.user.username
    })

def handle_video_upload(request):
    video_file = request.FILES['video']
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
    filename = fs.save(video_file.name, video_file)
    video_path = fs.path(filename)
    
    # Process video for license plate detection
    results = detector.process_video_file(video_path)
    
    # Save results to database
    for result in results:
        if result['plate_text'] != 'UNKNOWN':
            # Save the cropped plate image
            if result['plate_crop'] is not None:
                crop_filename = f"plate_{request.user.id}_{len(results)}_{result['timestamp']:.1f}.jpg"
                crop_path = os.path.join(settings.MEDIA_ROOT, 'plates', crop_filename)
                os.makedirs(os.path.dirname(crop_path), exist_ok=True)
                cv2.imwrite(crop_path, result['plate_crop'])
            else:
                crop_filename = None
            
            VehicleLog.objects.create(
                user=request.user,
                plate_text=result['plate_text'],
                vendor=result['vehicle_type'],
                video_filename=filename,
                image_filename=crop_filename,
                status='unknown'
            )
    
    messages.success(request, f'Video processed successfully! Found {len(results)} license plates.')
    return redirect('dashboard')

@login_required
def admin_dashboard(request):
    # Check if user is admin
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_admin:
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        return redirect('dashboard')
    
    plates = VehicleLog.objects.all().order_by('-timestamp')
    
    return render(request, 'plate_detector/admin_dashboard.html', {
        'plates': plates
    })

@login_required
def process_video(request):
    if request.method == 'POST' and 'video' in request.FILES:
        return JsonResponse(handle_video_upload_ajax(request))
    
    return JsonResponse({'error': 'Invalid request'})

def handle_video_upload_ajax(request):
    try:
        video_file = request.FILES['video']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
        filename = fs.save(video_file.name, video_file)
        video_path = fs.path(filename)
        
        results = detector.process_video_file(video_path)
        
        processed_results = []
        for i, result in enumerate(results):
            if result['plate_text'] != 'UNKNOWN':
                crop_filename = None
                if result['plate_crop'] is not None:
                    crop_filename = f"plate_{request.user.id}_{i}_{result['timestamp']:.1f}.jpg"
                    crop_path = os.path.join(settings.MEDIA_ROOT, 'plates', crop_filename)
                    os.makedirs(os.path.dirname(crop_path), exist_ok=True)
                    cv2.imwrite(crop_path, result['plate_crop'])
                
                log_entry = VehicleLog.objects.create(
                    user=request.user,
                    plate_text=result['plate_text'],
                    vendor=result['vehicle_type'],
                    video_filename=filename,
                    image_filename=crop_filename,
                    status='unknown'
                )
                
                processed_results.append({
                    'plate_text': result['plate_text'],
                    'vehicle_type': result['vehicle_type'],
                    'timestamp': result['timestamp'],
                    'id': log_entry.id
                })
        
        return {
            'success': True,
            'message': f'Video processed successfully! Found {len(processed_results)} license plates.',
            'results': processed_results
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
