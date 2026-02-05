"""
Admin Panel Admin Configuration
"""

from django.contrib import admin
from .models import MunicipalOfficer


@admin.register(MunicipalOfficer)
class MunicipalOfficerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Municipal Officer
    """
    
    list_display = ['employee_id', 'user', 'designation', 'role', 'department', 'is_active']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['employee_id', 'user__username', 'designation']
    ordering = ['employee_id']
