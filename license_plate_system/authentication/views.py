from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from vehicle_control.models import UserProfile
import json

def landing_page(request):
    """Modern landing page with 3D animations"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'authentication/landing.html')

def login_view(request):
    """Enhanced login page with modern UI"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Browser close
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect based on user type
            if user.is_staff or user.is_superuser:
                return redirect('dashboard:admin_dashboard')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'authentication/login.html')

def register_view(request):
    """Comprehensive registration system"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        terms_accepted = request.POST.get('terms_accepted')
        
        # Validation
        if not all([username, email, password1, password2, first_name, last_name]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'authentication/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'authentication/register.html')
        
        if not terms_accepted:
            messages.error(request, 'Please accept the terms and conditions.')
            return render(request, 'authentication/register.html')
        
        # Check if username or email exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'authentication/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'authentication/register.html')
        
        # Create user
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    phone_number=phone_number,
                    address=address
                )
                
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('authentication:login')
                
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
    
    return render(request, 'authentication/register.html')

@csrf_exempt
def check_username(request):
    """AJAX endpoint to check username availability"""
    if request.method == 'POST':
        username = json.loads(request.body).get('username', '')
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'available': not exists})
    return JsonResponse({'available': False})

@csrf_exempt  
def check_email(request):
    """AJAX endpoint to check email availability"""
    if request.method == 'POST':
        email = json.loads(request.body).get('email', '')
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'available': not exists})
    return JsonResponse({'available': False})

def logout_view(request):
    """Enhanced logout with confirmation"""
    user_name = request.user.first_name or request.user.username if request.user.is_authenticated else "User"
    logout(request)
    messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
    return redirect('authentication:landing')

@login_required
def profile_view(request):
    """User profile management"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('authentication:profile')
    
    return render(request, 'authentication/profile.html', {'profile': profile})

def forgot_password(request):
    """Forgot password page (placeholder)"""
    return render(request, 'authentication/forgot_password.html')

def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'authentication/privacy_policy.html')

def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'authentication/terms_of_service.html')
