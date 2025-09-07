from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, AuthorizedVehicle, AccessLog, 
    VehicleDetection, SystemSettings, GateControlLog
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_premium', 'subscription_end_date')
    list_filter = ('is_premium', 'subscription_end_date')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('user',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(AuthorizedVehicle)
class AuthorizedVehicleAdmin(admin.ModelAdmin):
    list_display = (
        'plate_number', 'owner_name', 'vehicle_type', 
        'access_level', 'is_active', 'registered_date', 'expiry_status'
    )
    list_filter = ('vehicle_type', 'access_level', 'is_active', 'registered_date')
    search_fields = ('plate_number', 'owner_name', 'owner_contact')
    readonly_fields = ('registered_date',)
    date_hierarchy = 'registered_date'
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('plate_number', 'vehicle_type', 'vehicle_brand', 'vehicle_model', 'vehicle_color')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'owner_contact')
        }),
        ('Access Control', {
            'fields': ('access_level', 'is_active', 'expiry_date')
        }),
        ('Administrative', {
            'fields': ('registered_by', 'registered_date', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def expiry_status(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.expiry_date:
            return format_html('<span style="color: orange;">Valid until {}</span>', 
                             obj.expiry_date.strftime('%Y-%m-%d'))
        return format_html('<span style="color: green;">No expiry</span>')
    
    expiry_status.short_description = 'Status'

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'plate_number', 'authorized_status', 
        'gate_action', 'confidence', 'owner_link'
    )
    list_filter = ('authorized', 'gate_action', 'timestamp')
    search_fields = ('plate_number',)
    readonly_fields = ('timestamp', 'detection_image_preview')
    date_hierarchy = 'timestamp'
    
    def authorized_status(self, obj):
        if obj.authorized:
            return format_html('<span style="color: green;">✅ Authorized</span>')
        return format_html('<span style="color: red;">❌ Denied</span>')
    
    authorized_status.short_description = 'Status'
    
    def owner_link(self, obj):
        if obj.vehicle:
            url = reverse('admin:vehicle_control_authorizedvehicle_change', args=[obj.vehicle.id])
            return format_html('<a href="{}">{}</a>', url, obj.vehicle.owner_name)
        return '-'
    
    owner_link.short_description = 'Owner'
    
    def detection_image_preview(self, obj):
        if obj.detection_image:
            return format_html('<img src="{}" width="200" height="auto" />', obj.detection_image.url)
        return 'No image'
    
    detection_image_preview.short_description = 'Detection Image'

@admin.register(VehicleDetection)
class VehicleDetectionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'uploaded_by', 'plate_text', 'status', 
        'confidence_score', 'upload_timestamp'
    )
    list_filter = ('status', 'upload_timestamp')
    search_fields = ('plate_text', 'uploaded_by__username')
    readonly_fields = ('upload_timestamp', 'processed_at')
    
    fieldsets = (
        ('Detection Results', {
            'fields': ('plate_text', 'vehicle_type', 'confidence_score', 'status')
        }),
        ('Media Files', {
            'fields': ('video_file', 'detection_image')
        }),
        ('Processing Info', {
            'fields': ('uploaded_by', 'upload_timestamp', 'processed_at', 'processing_notes')
        }),
    )

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('setting_name', 'setting_value', 'last_modified', 'modified_by')
    search_fields = ('setting_name', 'description')
    readonly_fields = ('last_modified',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('modified_by')

@admin.register(GateControlLog)
class GateControlLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'operation', 'triggered_by', 
        'duration_seconds', 'related_access'
    )
    list_filter = ('operation', 'timestamp')
    search_fields = ('triggered_by__username',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def related_access(self, obj):
        if obj.related_access_log:
            return f"{obj.related_access_log.plate_number}"
        return '-'
    
    related_access.short_description = 'Related Access'

# Customize admin site
admin.site.site_header = "LicenseGuard AI Administration"
admin.site.site_title = "LicenseGuard Admin"
admin.site.index_title = "Welcome to LicenseGuard AI Admin Panel"
