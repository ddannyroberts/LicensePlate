from django.urls import path
from . import views

app_name = 'vehicle_control'

urlpatterns = [
    # User routes
    path('register-plate/', views.register_plate, name='register_plate'),
    path('my-plates/', views.my_plates, name='my_plates'),
    path('delete-plate/<int:plate_id>/', views.delete_plate, name='delete_plate'),
    
    # Admin routes
    path('admin/upload-video/', views.admin_upload_video, name='admin_upload_video'),
    path('admin/video-list/', views.admin_video_list, name='admin_video_list'),
    path('admin/video-detail/<int:video_id>/', views.admin_video_detail, name='admin_video_detail'),
    path('admin/plate-history/', views.admin_plate_history, name='admin_plate_history'),
    
    # Image download/view
    path('admin/download-image/<str:image_type>/<int:image_id>/', views.download_plate_image, name='download_plate_image'),
    path('admin/view-image/<str:image_type>/<int:image_id>/', views.view_plate_image, name='view_plate_image'),
]