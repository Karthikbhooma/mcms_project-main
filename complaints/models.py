"""
Complaints Models
Core complaint management with audit trail
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from departments.models import Department
import random
import string


def generate_complaint_id():
    """
    Generate unique complaint ID
    Format: MCMS-YYYY-XXXXXXXX
    """
    year = timezone.now().year
    random_part = ''.join(random.choices(string.digits, k=8))
    return f"MCMS-{year}-{random_part}"


def complaint_proof_upload_path(instance, filename):
    """
    Generate upload path for complaint proof files
    """
    return f'complaints/{instance.complaint_id}/{filename}'


def resolution_proof_upload_path(instance, filename):
    return f'complaints/{instance.complaint_id}/resolution/{filename}'


class Complaint(models.Model):
    """
    Complaint Model - Immutable after submission
    Complete complaint lifecycle tracking
    """
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    # Unique identifiers
    complaint_id = models.CharField(
        max_length=50,
        unique=True,
        default=generate_complaint_id,
        editable=False,
        db_index=True
    )
    
    # Citizen information
    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='complaints'
    )
    
    # Department
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='complaints'
    )
    
    # Location details
    ward_number = models.CharField(max_length=10)
    area = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200, blank=True)
    
    # Complaint details
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Proof attachment
    proof_file = models.FileField(
        upload_to=complaint_proof_upload_path,
        blank=True,
        null=True
    )
    
    # Status and workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED',
        db_index=True
    )
    
    # Official remarks from admin
    official_remarks = models.TextField(blank=True)
    
    # Assigned officer (municipal staff) handling the complaint
    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    # Resolution details provided by officer/admin when marking resolved
    resolution_notes = models.TextField(blank=True)

    # Proof for resolution (photo/document showing work done)
    resolution_proof = models.FileField(
        upload_to=resolution_proof_upload_path,
        blank=True,
        null=True
    )
    # Timestamps - Audit trail
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Status change timestamps
    reviewed_at = models.DateTimeField(null=True, blank=True)
    in_progress_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete flag (no actual deletion)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'complaints'
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['complaint_id']),
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['department', 'status']),
        ]
    
    def __str__(self):
        return f"{self.complaint_id} - {self.subject[:50]}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure complaint_id uniqueness
        """
        if not self.complaint_id:
            # Generate unique complaint ID
            while True:
                new_id = generate_complaint_id()
                if not Complaint.objects.filter(complaint_id=new_id).exists():
                    self.complaint_id = new_id
                    break
        
        super().save(*args, **kwargs)
    
    def get_status_display_class(self):
        """
        Return CSS class for status badge
        """
        status_classes = {
            'SUBMITTED': 'status-submitted',
            'UNDER_REVIEW': 'status-review',
            'IN_PROGRESS': 'status-progress',
            'RESOLVED': 'status-resolved',
            'CLOSED': 'status-closed',
        }
        return status_classes.get(self.status, 'status-default')
    
    def get_days_pending(self):
        """
        Calculate days since submission
        """
        if self.status in ['RESOLVED', 'CLOSED']:
            return 0
        
        delta = timezone.now() - self.submitted_at
        return delta.days
    
    def is_overdue(self, threshold_days=7):
        """
        Check if complaint is overdue
        """
        return self.get_days_pending() > threshold_days


class ComplaintStatusHistory(models.Model):
    """
    Complaint Status Change History - Audit Trail
    Immutable record of all status changes
    """
    
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    remarks = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'complaint_status_history'
        verbose_name = 'Status History'
        verbose_name_plural = 'Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.complaint.complaint_id} - {self.from_status} → {self.to_status}"


class ComplaintComment(models.Model):
    """
    Comments/Notes on complaints
    For internal tracking and communication
    """
    
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    comment_text = models.TextField()
    is_internal = models.BooleanField(default=True)  # Internal notes vs public
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'complaint_comments'
        verbose_name = 'Complaint Comment'
        verbose_name_plural = 'Complaint Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.complaint.complaint_id}"
