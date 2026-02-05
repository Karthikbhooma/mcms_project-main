"""
Accounts Admin Configuration
Django admin customization for Citizen model
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Citizen, LoginAttempt


@admin.register(Citizen)
class CitizenAdmin(UserAdmin):
    """
    Custom admin for Citizen model
    """
    
    list_display = ['username', 'email', 'mobile', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'mobile']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('username', 'email', 'mobile')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'mobile', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Admin for login attempts monitoring
    """
    
    list_display = ['username', 'ip_address', 'success', 'attempted_at']
    list_filter = ['success', 'attempted_at']
    search_fields = ['username', 'ip_address']
    ordering = ['-attempted_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
