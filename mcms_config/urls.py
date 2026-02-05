"""
URL Configuration for Municipal Complaint Management System
Government-grade routing architecture
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Django Admin (for superuser only)
    path('django-admin/', admin.site.urls),
    
    # Home Page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Citizen/User Module
    path('accounts/', include('accounts.urls')),
    
    # Complaint Module
    path('complaints/', include('complaints.urls')),
    
    # Admin Panel Module
    path('admin-panel/', include('adminpanel.urls')),
    
    # Department Module
    path('departments/', include('departments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'mcms_config.views.error_404'
handler500 = 'mcms_config.views.error_500'
