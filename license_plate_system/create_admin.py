#!/usr/bin/env python
"""
Script to create admin superuser quickly
Run: python create_admin.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'license_plate_system.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    """Create admin superuser if not exists"""
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    # Check if admin already exists
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        print("   To reset password, use: python manage.py changepassword admin")
        return False
    
    # Create superuser
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("✅ Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("\n   You can now login at: http://127.0.0.1:8000/auth/login/")
        return True
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

if __name__ == '__main__':
    create_admin()

