"""
Authentication URLs - Migrated from Flask routes
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Flask: @app.route('/')
    path('login/', views.login_view, name='login'),  # Flask: @app.route('/login')
    path('register/', views.register_view, name='register'),  # Flask: @app.route('/register')
    path('logout/', views.logout_view, name='logout'),  # Flask: @app.route('/logout')
]