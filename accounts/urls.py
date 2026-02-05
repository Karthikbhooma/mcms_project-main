"""
Accounts URL Configuration
Routing for citizen authentication
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration
    path('register/', views.citizen_register, name='register'),
    # OTP verification removed - users are verified on registration
    
    # Login/Logout
    path('login/', views.citizen_login, name='login'),
    path('logout/', views.citizen_logout, name='logout'),
    
    # CAPTCHA
    path('refresh-captcha/', views.refresh_captcha, name='refresh_captcha'),
]
