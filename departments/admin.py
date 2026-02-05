"""
Departments Admin Configuration
"""

from django.contrib import admin
from .models import Department, ComplaintCategory


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Department
    """
    
    list_display = ['code', 'name', 'head_of_department', 'contact_number', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'head_of_department']
    ordering = ['name']


@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Complaint Category
    """
    
    list_display = ['name', 'department', 'priority', 'is_active']
    list_filter = ['department', 'priority', 'is_active']
    search_fields = ['name', 'department__name']
    ordering = ['department', 'name']
