"""
URL configuration for license_plate_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import landing_page

# Import custom admin configuration
from .admin import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),  # All auth routes under /auth/
    path('', landing_page, name='home'),  # Root redirects to login or dashboard
    path('dashboard/', include('dashboard.urls')),
    path('vehicles/', include('vehicle_control.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
