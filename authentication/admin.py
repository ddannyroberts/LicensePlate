"""
Authentication admin configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_admin',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('is_admin',)}),
    )