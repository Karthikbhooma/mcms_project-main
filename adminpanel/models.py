"""
Admin Panel Models
Municipal officer and admin user management
"""

from django.db import models
from django.conf import settings


class MunicipalOfficer(models.Model):
    """
    Municipal Officer Model
    Extends Citizen model for admin users
    """
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Department Manager'),
        ('OFFICER', 'Municipal Officer'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='officer_profile'
    )
    
    employee_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OFFICER')
    designation = models.CharField(max_length=100)
    
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='officers'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'municipal_officers'
        verbose_name = 'Municipal Officer'
        verbose_name_plural = 'Municipal Officers'
    
    def __str__(self):
        return f"{self.user.username} - {self.designation}"
