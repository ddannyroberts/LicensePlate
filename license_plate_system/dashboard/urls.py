from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_dashboard, name='home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
]