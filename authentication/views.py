"""
Authentication views - Migrated from Flask routes
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from .models import User


def home_view(request):
    """Home page redirect - Migrated from Flask @app.route('/')"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'is_admin_user') and request.user.is_admin_user:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    return redirect('login')


@csrf_protect
def register_view(request):
    """
    User registration - Migrated from Flask register route

    Original Flask route:
    @app.route('/register', methods=['GET', 'POST'])
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'authentication/register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'authentication/register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password
        )
        messages.success(request, 'Registration successful!')
        return redirect('login')

    return render(request, 'authentication/register.html')


@csrf_protect
def login_view(request):
    """
    User login - Migrated from Flask login route

    Original Flask route:
    @app.route('/login', methods=['GET', 'POST'])
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect based on user type
            if hasattr(user, 'is_admin_user') and user.is_admin_user:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'authentication/login.html')


def logout_view(request):
    """
    User logout - Migrated from Flask logout route

    Original Flask route:
    @app.route('/logout')
    """
    logout(request)
    return redirect('login')