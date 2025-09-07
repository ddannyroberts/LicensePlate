from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    
    # AJAX endpoints
    path('api/check-username/', views.check_username, name='check_username'),
    path('api/check-email/', views.check_email, name='check_email'),
]