#!/usr/bin/env python
"""
Script to manage user roles in the system
Usage: python manage_roles.py [command] [username] [options]
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'license_plate_system.settings')
django.setup()

from django.contrib.auth.models import User

def list_users():
    """List all users with their roles"""
    users = User.objects.all().order_by('username')
    
    print("\n" + "="*80)
    print("USER ROLES LIST")
    print("="*80)
    print(f"{'Username':<20} {'Email':<30} {'Staff':<8} {'Superuser':<12} {'Active':<8}")
    print("-"*80)
    
    for user in users:
        staff = "✓" if user.is_staff else "✗"
        superuser = "✓" if user.is_superuser else "✗"
        active = "✓" if user.is_active else "✗"
        print(f"{user.username:<20} {user.email or 'N/A':<30} {staff:<8} {superuser:<12} {active:<8}")
    
    print("="*80)
    print(f"Total users: {users.count()}")
    print()

def make_admin(username):
    """Make user an admin (staff)"""
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ User '{username}' is now an admin (staff + superuser)")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def remove_admin(username):
    """Remove admin privileges from user"""
    try:
        user = User.objects.get(username=username)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        print(f"✅ Admin privileges removed from '{username}'")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def make_staff(username):
    """Make user staff (but not superuser)"""
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.save()
        print(f"✅ User '{username}' is now staff")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def remove_staff(username):
    """Remove staff status from user"""
    try:
        user = User.objects.get(username=username)
        user.is_staff = False
        user.save()
        print(f"✅ Staff status removed from '{username}'")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def activate_user(username):
    """Activate user account"""
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        print(f"✅ User '{username}' is now active")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def deactivate_user(username):
    """Deactivate user account"""
    try:
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()
        print(f"✅ User '{username}' is now inactive")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def show_help():
    """Show help message"""
    print("""
🔐 User Role Management Script

Usage: python manage_roles.py [command] [username]

Commands:
  list                    - List all users and their roles
  admin [username]        - Make user admin (staff + superuser)
  remove-admin [username] - Remove admin privileges
  staff [username]        - Make user staff only
  remove-staff [username] - Remove staff status
  activate [username]     - Activate user account
  deactivate [username]   - Deactivate user account
  help                    - Show this help message

Examples:
  python manage_roles.py list
  python manage_roles.py admin john
  python manage_roles.py remove-admin john
  python manage_roles.py activate john
    """)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_users()
    elif command == 'admin' and len(sys.argv) > 2:
        make_admin(sys.argv[2])
    elif command == 'remove-admin' and len(sys.argv) > 2:
        remove_admin(sys.argv[2])
    elif command == 'staff' and len(sys.argv) > 2:
        make_staff(sys.argv[2])
    elif command == 'remove-staff' and len(sys.argv) > 2:
        remove_staff(sys.argv[2])
    elif command == 'activate' and len(sys.argv) > 2:
        activate_user(sys.argv[2])
    elif command == 'deactivate' and len(sys.argv) > 2:
        deactivate_user(sys.argv[2])
    elif command == 'help':
        show_help()
    else:
        print("❌ Invalid command or missing username")
        show_help()

if __name__ == '__main__':
    main()

