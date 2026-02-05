"""
Complaints URL Configuration
"""

from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.citizen_dashboard, name='dashboard'),
    
    # Submit complaint
    path('submit/', views.submit_complaint, name='submit'),
    
    # View complaint detail
    path('detail/<str:complaint_id>/', views.complaint_detail, name='detail'),
    
    # Track complaint
    path('track/', views.track_complaint, name='track'),
]
