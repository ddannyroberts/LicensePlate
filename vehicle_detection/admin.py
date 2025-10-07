"""
Vehicle Detection admin configuration
"""
from django.contrib import admin
from .models import VehicleLog, AuthorizedVehicle, AccessLog, VehicleStatus, SystemStats


@admin.register(VehicleLog)
class VehicleLogAdmin(admin.ModelAdmin):
    list_display = (
        'plate_text', 'user', 'vendor', 'category', 'status',
        'confidence', 'timestamp'
    )
    list_filter = ('status', 'category', 'timestamp', 'confidence')
    search_fields = ('plate_text', 'vendor', 'model', 'province')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    fieldsets = (
        ('Detection Info', {
            'fields': ('user', 'plate_text', 'confidence', 'status')
        }),
        ('Vehicle Details', {
            'fields': ('vendor', 'model', 'color', 'province', 'category')
        }),
        ('Media Files', {
            'fields': ('image_filename', 'video_filename')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(AuthorizedVehicle)
class AuthorizedVehicleAdmin(admin.ModelAdmin):
    list_display = (
        'plate_number', 'owner_name', 'vehicle_type',
        'access_level', 'is_active', 'registered_date'
    )
    list_filter = ('vehicle_type', 'access_level', 'is_active', 'registered_date')
    search_fields = ('plate_number', 'owner_name', 'phone_number')
    readonly_fields = ('registered_date',)
    ordering = ('-registered_date',)

    fieldsets = (
        ('Vehicle Information', {
            'fields': ('plate_number', 'vehicle_type')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'phone_number')
        }),
        ('Access Control', {
            'fields': ('access_level', 'is_active')
        }),
        ('Additional Info', {
            'fields': ('notes', 'registered_date')
        }),
    )


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = (
        'plate_number', 'authorized', 'gate_action', 'entry_type',
        'confidence', 'detection_source', 'timestamp'
    )
    list_filter = (
        'authorized', 'gate_action', 'entry_type',
        'detection_source', 'timestamp'
    )
    search_fields = ('plate_number',)
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    fieldsets = (
        ('Access Attempt', {
            'fields': ('plate_number', 'authorized', 'gate_action', 'entry_type')
        }),
        ('Detection Details', {
            'fields': ('confidence', 'detection_source', 'authorized_vehicle')
        }),
        ('Owner Information', {
            'fields': ('owner_info',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(VehicleStatus)
class VehicleStatusAdmin(admin.ModelAdmin):
    list_display = (
        'plate_number', 'status', 'entry_time', 'exit_time',
        'duration', 'last_updated'
    )
    list_filter = ('status', 'last_updated')
    search_fields = ('plate_number',)
    readonly_fields = ('last_updated', 'duration')
    ordering = ('-last_updated',)


@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'total_entries', 'total_exits', 'authorized_entries',
        'unauthorized_attempts', 'vehicles_inside', 'peak_occupancy'
    )
    list_filter = ('date',)
    readonly_fields = ('last_updated',)
    ordering = ('-date',)

    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Traffic Statistics', {
            'fields': ('total_entries', 'total_exits', 'authorized_entries', 'unauthorized_attempts')
        }),
        ('Occupancy', {
            'fields': ('vehicles_inside', 'peak_occupancy')
        }),
        ('Last Updated', {
            'fields': ('last_updated',)
        }),
    )