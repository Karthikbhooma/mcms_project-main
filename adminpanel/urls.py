"""
Admin Panel URL Configuration
"""

from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    # Complaints management
    path('complaints/', views.all_complaints, name='all_complaints'),
    path('complaints/<str:complaint_id>/', views.complaint_detail_admin, name='complaint_detail'),
    path('complaints/<str:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('complaints/<str:complaint_id>/delete/', views.delete_complaint, name='delete_complaint'),
    
    # Department-wise complaints
    path('department/<str:dept_code>/', views.department_complaints, name='department_complaints'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]
