from django.urls import path
from . import views

app_name = 'vehicle_control'

urlpatterns = [
    path('authorized/', views.authorized_vehicles, name='authorized_vehicles'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('remove-vehicle/<int:vehicle_id>/', views.remove_vehicle, name='remove_vehicle'),
    path('access-logs/', views.access_logs, name='access_logs'),
    path('upload-video/', views.upload_video, name='upload_video'),
    path('process-video/<int:detection_id>/', views.process_video, name='process_video'),
    path('test-gate/', views.test_gate_control, name='test_gate'),
    
    # API endpoints
    path('api/video-progress/<int:detection_id>/', views.video_progress_api, name='video_progress_api'),
    path('api/gate-status/', views.gate_status_api, name='gate_status_api'),
]