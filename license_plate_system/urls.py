"""
URL configuration for license_plate_system project.
Migrated from Flask routes.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('dashboard/', include('vehicle_detection.urls')),
    path('access-control/', include('access_control.urls')),
    path('api/arduino/', include('arduino_integration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "License Plate Recognition System"
admin.site.site_title = "LPR Admin"
admin.site.index_title = "Welcome to License Plate Recognition System Administration"