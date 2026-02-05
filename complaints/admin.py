"""
Complaints Admin Configuration
"""

from django.contrib import admin
from .models import Complaint, ComplaintStatusHistory, ComplaintComment


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    """
    Admin configuration for Complaint model
    """
    
    list_display = [
        'complaint_id', 'citizen', 'department', 'subject', 
        'status', 'submitted_at', 'get_days_pending'
    ]
    list_filter = ['status', 'department', 'submitted_at', 'is_archived']
    search_fields = ['complaint_id', 'subject', 'citizen__username', 'citizen__email']
    readonly_fields = [
        'complaint_id', 'citizen', 'submitted_at', 'last_updated',
        'reviewed_at', 'in_progress_at', 'resolved_at', 'closed_at'
    ]
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Complaint Information', {
            'fields': ('complaint_id', 'citizen', 'department')
        }),
        ('Location Details', {
            'fields': ('ward_number', 'area', 'landmark')
        }),
        ('Complaint Details', {
            'fields': ('subject', 'description', 'proof_file')
        }),
        ('Status & Remarks', {
            'fields': ('status', 'official_remarks')
        }),
        ('Timestamps', {
            'fields': (
                'submitted_at', 'reviewed_at', 'in_progress_at',
                'resolved_at', 'closed_at', 'last_updated'
            )
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of complaints
        return False


@admin.register(ComplaintStatusHistory)
class ComplaintStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin for status history (read-only)
    """
    
    list_display = ['complaint', 'from_status', 'to_status', 'changed_by', 'changed_at']
    list_filter = ['to_status', 'changed_at']
    search_fields = ['complaint__complaint_id']
    readonly_fields = ['complaint', 'from_status', 'to_status', 'changed_by', 'remarks', 'changed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    """
    Admin for complaint comments
    """
    
    list_display = ['complaint', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['complaint__complaint_id', 'comment_text']
    readonly_fields = ['created_at']
