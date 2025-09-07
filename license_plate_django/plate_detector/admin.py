from django.contrib import admin
from .models import VehicleLog, UserProfile

@admin.register(VehicleLog)
class VehicleLogAdmin(admin.ModelAdmin):
    list_display = ['plate_text', 'user', 'vendor', 'model', 'status', 'timestamp']
    list_filter = ['status', 'vendor', 'timestamp']
    search_fields = ['plate_text', 'user__username', 'vendor', 'model']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_admin']
    list_filter = ['is_admin']
    search_fields = ['user__username']
