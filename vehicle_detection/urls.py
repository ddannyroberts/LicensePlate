"""
Vehicle Detection URLs - Migrated from Flask routes
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # Flask: @app.route('/dashboard')
    path('process-video/', views.process_video_api, name='process_video_api'),  # Flask: @app.route('/process-video')
    path('api/detect_frame/', views.detect_frame_api, name='detect_frame_api'),  # Flask: @app.route('/api/detect_frame')
    path('api/save_detected_plate/', views.save_detected_plate_api, name='save_detected_plate_api'),  # Flask: @app.route('/api/save_detected_plate')
]